"""数据模型：用户配置（Screen）与运行态（Runtime）严格分离。

分成两个模型不是为了好看 —— 配置是"用户意图"，只在用户改设置时写盘；运行态是
"观察结果"，每次进程事件都会变。混在一起会让每次进程启动都重写配置文件。

身份标识用 (name, port)，不用 pid —— pid 会复用、会变、重启后毫无意义。
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum

from . import constants as C
from .i18n import tr


class ScreenState(Enum):
    """一个屏幕在界面上的呈现状态。"""

    RUNNING = "running"      # 进程存活且身份匹配
    STOPPED = "stopped"      # 用户主动停止，且确实没在跑
    CRASHED = "crashed"      # 期望它运行，但进程不在了
    STARTING = "starting"    # 正在启动，等待 KWin 输出出现
    FAILED = "failed"        # 启动失败（端口占用 / portal 拒绝 / 超时）
    UNMANAGED = "unmanaged"  # 外部启动的进程，尚未纳入管理

    @property
    def label(self) -> str:
        """界面显示名。每次访问都查当前语言（自绘行每帧都会读它），
        所以必须是普通 str —— 测试脚本会直接 print 它。"""
        return tr({
            ScreenState.RUNNING: "Running",
            ScreenState.STOPPED: "Stopped",
            ScreenState.CRASHED: "Exited unexpectedly",
            ScreenState.STARTING: "Starting",
            ScreenState.FAILED: "Failed to start",
            ScreenState.UNMANAGED: "Unmanaged",
        }[self])

    @property
    def is_active(self) -> bool:
        """占用端口/资源的状态。"""
        return self in (ScreenState.RUNNING, ScreenState.STARTING)


@dataclass
class Screen:
    """一个虚拟屏的用户配置。不含密码 —— 密码存在 Secret Service 里，以 id 为键。"""

    name: str
    width: int = C.DEFAULT_RESOLUTION[0]
    height: int = C.DEFAULT_RESOLUTION[1]
    scale: float = C.DEFAULT_SCALE
    port: int = C.DEFAULT_PORT
    notes: str = ""

    # 单一"期望运行"标志：既驱动登录自启，也驱动崩溃横幅。
    # 不再单独设 autostart 字段 —— 两者语义完全重合，两个开关只会互相矛盾。
    desired_running: bool = False

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: float = field(default_factory=time.time)

    # --- 派生属性 -----------------------------------------------------------
    @property
    def resolution(self) -> str:
        """传给 --resolution 的形式，如 '2736x1824'。"""
        return f"{self.width}x{self.height}"

    @property
    def resolution_display(self) -> str:
        return f"{self.width}×{self.height}"

    @property
    def aspect(self) -> float:
        return self.width / self.height if self.height else 16 / 9

    @property
    def connector_name(self) -> str:
        """KWin 的输出名。krfb 用 'Virtual-' + name 作为 connector name。"""
        return f"Virtual-{self.name}"

    def matches_process(self, name: str | None, port: int | None) -> bool:
        """身份匹配：按 (name, port) 判断"是不是同一个屏幕"。"""
        return name == self.name and port == self.port

    # --- 序列化 -------------------------------------------------------------
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "width": self.width,
            "height": self.height,
            "scale": self.scale,
            "port": self.port,
            "notes": self.notes,
            "desired_running": self.desired_running,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Screen":
        """宽容解析：缺失字段用默认值，坏数据不让整个文件读不出来。"""
        return cls(
            # 数据默认值：一旦被保存就会以当时的语言写进 screens.json
            # （属于"写时冻结"，和 manager.adopt 的 notes 同一类）。
            name=str(d.get("name", tr("Unnamed"))),
            width=int(d.get("width", C.DEFAULT_RESOLUTION[0])),
            height=int(d.get("height", C.DEFAULT_RESOLUTION[1])),
            scale=float(d.get("scale", C.DEFAULT_SCALE)),
            port=int(d.get("port", C.DEFAULT_PORT)),
            notes=str(d.get("notes", "")),
            desired_running=bool(d.get("desired_running", False)),
            id=str(d.get("id") or uuid.uuid4()),
            created_at=float(d.get("created_at", time.time())),
        )


@dataclass
class Runtime:
    """一个虚拟屏的运行态观察结果。持久化在 runtime.json，与配置分文件。"""

    pid: int | None = None
    starttime: int | None = None

    # KWin 实际生效的值 —— 实测 --scale 会被覆写（请求 1.5 实际 1.75），
    # 所以必须回读而不是相信请求值。
    actual_width: int | None = None
    actual_height: int | None = None
    actual_scale: float | None = None

    last_started_at: float | None = None
    last_exit_at: float | None = None
    consecutive_failures: int = 0
    last_error: str = ""

    @property
    def actual_resolution_display(self) -> str | None:
        if self.actual_width and self.actual_height:
            return f"{self.actual_width}×{self.actual_height}"
        return None

    def scale_overridden(self, requested: float) -> bool:
        """请求的 scale 是否被 KWin 改掉了。"""
        return self.actual_scale is not None and abs(self.actual_scale - requested) > 0.01

    def to_dict(self) -> dict:
        return {
            "pid": self.pid,
            "starttime": self.starttime,
            "actual_width": self.actual_width,
            "actual_height": self.actual_height,
            "actual_scale": self.actual_scale,
            "last_started_at": self.last_started_at,
            "last_exit_at": self.last_exit_at,
            "consecutive_failures": self.consecutive_failures,
            "last_error": self.last_error,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Runtime":
        def _opt_int(v):
            try:
                return int(v) if v is not None else None
            except (TypeError, ValueError):
                return None

        def _opt_float(v):
            try:
                return float(v) if v is not None else None
            except (TypeError, ValueError):
                return None

        return cls(
            pid=_opt_int(d.get("pid")),
            starttime=_opt_int(d.get("starttime")),
            actual_width=_opt_int(d.get("actual_width")),
            actual_height=_opt_int(d.get("actual_height")),
            actual_scale=_opt_float(d.get("actual_scale")),
            last_started_at=_opt_float(d.get("last_started_at")),
            last_exit_at=_opt_float(d.get("last_exit_at")),
            consecutive_failures=_opt_int(d.get("consecutive_failures")) or 0,
            last_error=str(d.get("last_error") or ""),
        )


@dataclass
class ProcInfo:
    """从 /proc 读出来的一个 krfb-virtualmonitor 进程。"""

    pid: int
    starttime: int
    exe: str
    argv: tuple[str, ...]
    name: str | None
    port: int | None
    resolution: str | None
    scale: float | None
    password: str | None

    @property
    def exe_is_deleted(self) -> bool:
        """包升级后旧进程的 exe 链接会带 ' (deleted)' 后缀。"""
        return self.exe.endswith(" (deleted)")
