"""持久化：用户配置与运行态**分文件**存放，原子写入。

为什么分两个文件：配置是"用户意图"，只在用户改设置时写盘；运行态是"观察结果"，
每次进程启动/退出都要更新。合在一起会让每次进程事件都重写配置文件，而且两个 GUI
实例会互相覆盖对方的更新（原子写能防文件损坏，防不住丢更新）。
"""

from __future__ import annotations

import contextlib
import json
import os
import tempfile
import time
from pathlib import Path

from . import constants as C
from .i18n import trf
from .models import Runtime, Screen

SCHEMA_VERSION = 1


def _fsync_dir(path: Path) -> None:
    """fsync 父目录，确保目录项本身也落盘（否则 rename 可能丢失）。"""
    try:
        fd = os.open(str(path), os.O_DIRECTORY)
    except OSError:
        return
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def atomic_write_json(path: Path, payload: object) -> None:
    """原子写 JSON：临时文件 → fsync → rename → fsync 父目录。

    权限固定 0600 —— 文件里虽然不含密码明文，但有 keyring 引用和进程运行态。
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(tmp, 0o600)
        os.replace(tmp, path)
        _fsync_dir(path.parent)
    except BaseException:
        with contextlib.suppress(OSError):
            os.unlink(tmp)
        raise


def read_json(path: Path) -> object | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeError):
        return None


class Store:
    """screens.json（配置）+ runtime.json（运行态）的读写门面。

    解析策略是"尽可能宽容"：单个屏幕记录坏掉不应该让整个文件读不出来。
    """

    def __init__(self, screens_file: Path | None = None, runtime_file: Path | None = None) -> None:
        self.screens_file = screens_file or C.SCREENS_FILE
        self.runtime_file = runtime_file or C.RUNTIME_FILE
        self.screens: dict[str, Screen] = {}
        self.runtimes: dict[str, Runtime] = {}
        # 读取失败时的原因，界面要如实告知用户而不是默默用空列表
        self.load_error: str = ""

    # --- 读取 ---------------------------------------------------------------
    def load(self) -> None:
        self.load_error = ""
        self._load_screens()
        self._load_runtimes()

    def _load_screens(self) -> None:
        raw = read_json(self.screens_file)
        if raw is None:
            # 文件不存在是正常情况（首次运行）；只有存在但读不出来才是错误
            if self.screens_file.exists():
                self.load_error = trf("Cannot parse the config file: {path}",
                                      path=self.screens_file)
            self.screens = {}
            return

        if isinstance(raw, dict):
            entries = raw.get("screens", [])
            version = raw.get("version")
            if version is not None and version != SCHEMA_VERSION:
                self.load_error = trf(
                    "Config version {found} doesn't match the expected {expected}; "
                    "loaded on a best-effort basis",
                    found=version, expected=SCHEMA_VERSION,
                )
        elif isinstance(raw, list):
            # 容忍无信封的裸列表
            entries = raw
        else:
            self.load_error = trf("Unrecognized config format: {path}",
                                  path=self.screens_file)
            entries = []

        screens: dict[str, Screen] = {}
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            try:
                screen = Screen.from_dict(entry)
            except (TypeError, ValueError):
                continue
            screens[screen.id] = screen
        self.screens = screens

    def _load_runtimes(self) -> None:
        raw = read_json(self.runtime_file)
        runtimes: dict[str, Runtime] = {}
        if isinstance(raw, dict):
            for sid, entry in (raw.get("runtimes") or {}).items():
                if isinstance(entry, dict):
                    runtimes[str(sid)] = Runtime.from_dict(entry)
        self.runtimes = runtimes

    # --- 写入 ---------------------------------------------------------------
    def save_screens(self) -> None:
        payload = {
            "version": SCHEMA_VERSION,
            "screens": [s.to_dict() for s in self.sorted_screens()],
        }
        atomic_write_json(self.screens_file, payload)

    def save_runtimes(self) -> None:
        payload = {
            "version": SCHEMA_VERSION,
            "runtimes": {sid: rt.to_dict() for sid, rt in self.runtimes.items()},
        }
        atomic_write_json(self.runtime_file, payload)

    # --- 屏幕操作 -----------------------------------------------------------
    def sorted_screens(self) -> list[Screen]:
        return sorted(self.screens.values(), key=lambda s: (s.port, s.name))

    def get(self, screen_id: str) -> Screen | None:
        return self.screens.get(screen_id)

    def add(self, screen: Screen) -> None:
        self.screens[screen.id] = screen
        self.save_screens()

    def remove(self, screen_id: str) -> Screen | None:
        screen = self.screens.pop(screen_id, None)
        self.runtimes.pop(screen_id, None)
        if screen is not None:
            self.save_screens()
            self.save_runtimes()
        return screen

    def runtime_for(self, screen_id: str, *, create: bool = True) -> Runtime:
        rt = self.runtimes.get(screen_id)
        if rt is None and create:
            rt = Runtime()
            self.runtimes[screen_id] = rt
        return rt or Runtime()

    def prune_runtimes(self) -> None:
        """清掉已删除屏幕留下的运行态残留。"""
        stale = [sid for sid in self.runtimes if sid not in self.screens]
        for sid in stale:
            del self.runtimes[sid]

    # --- 校验辅助 -----------------------------------------------------------
    def name_taken(self, name: str, *, exclude_id: str | None = None) -> bool:
        """KWin 的 connector 名就是 Virtual-<name>，所以名字必须唯一。"""
        return any(
            s.name == name and s.id != exclude_id for s in self.screens.values()
        )

    def port_taken(self, port: int, *, exclude_id: str | None = None) -> bool:
        return any(
            s.port == port and s.id != exclude_id for s in self.screens.values()
        )

    def next_free_port(self) -> int | None:
        """从默认端口起找一个既没被本程序分配、也没被系统占用的端口。"""
        from .proctools import listening_ports

        used = listening_ports()
        for port in range(C.PORT_MIN, C.PORT_MAX + 1):
            if port not in used and not self.port_taken(port):
                return port
        return None

    def mark_started(self, screen_id: str, pid: int, starttime: int) -> None:
        rt = self.runtime_for(screen_id)
        rt.pid = pid
        rt.starttime = starttime
        rt.last_started_at = time.time()
        rt.last_error = ""
        self.save_runtimes()

    def mark_stopped(self, screen_id: str, *, error: str = "") -> None:
        rt = self.runtime_for(screen_id)
        rt.pid = None
        rt.starttime = None
        rt.actual_width = None
        rt.actual_height = None
        rt.actual_scale = None
        rt.last_exit_at = time.time()
        if error:
            rt.last_error = error
            rt.consecutive_failures += 1
        self.save_runtimes()

    def note_error(self, screen_id: str, error: str) -> None:
        """只记错误，**不动**进程身份 —— 用于"进程还活着，但校验没过"。

        与 mark_stopped 的区别就是那几个身份字段：mark_stopped 清掉 pid/starttime，
        那是给"进程确实没了"用的。进程还活着时把身份清掉，它就变成谁也认不出的
        孤儿，只能靠「扫描」重新纳管。
        """
        rt = self.runtime_for(screen_id)
        rt.last_error = error
        rt.consecutive_failures += 1
        self.save_runtimes()
