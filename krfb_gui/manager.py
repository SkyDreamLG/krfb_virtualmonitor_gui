"""进程生命周期管理：启动、停止、状态判定、认领外部进程。

两条核心约束的实现都落在这里：

  约束 1「关闭 GUI 不影响虚拟屏」—— `start_new_session=True` 让子进程成为独立会话
      首进程，脱离 GUI 的进程组；再配合环境变量白名单（见 envtools.child_env）
      避免继承到会绑错 libQt6 的 ROS/CUDA 变量。

  约束 2「重开 GUI 继续管理」—— 身份用 (name, port)（持久、跨重启可比对），
      存活用 pidfd + starttime（防 PID 复用）。并主动扫描 /proc 认领非本程序启动的
      进程，让用户手敲的命令行也能一键纳管。

本模块**刻意不 import Qt**，保持可单独测试。异步等待交给 UI 用 QTimer 轮询，
避免引入线程复杂度。
"""

from __future__ import annotations

import os
import signal
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

from . import constants as C
from . import envtools, kscreen, proctools
from .i18n import tr, trf
from .models import ProcInfo, Runtime, Screen, ScreenState
from .secrets import Secrets
from .store import Store


@dataclass
class SpawnResult:
    ok: bool
    pid: int | None = None
    starttime: int | None = None
    error: str = ""


def build_argv(screen: Screen, password: str) -> list[str]:
    """把 Screen 翻译成 krfb-virtualmonitor 的命令行。

    krfb-virtualmonitor 的全部参数就是这 5 个（已核对 --help）：这是它暴露的
    完整能力面。
    """
    binary = proctools.krfb_binary() or C.KRFB_BIN
    return [
        binary,
        "--name", screen.name,
        "--resolution", screen.resolution,
        "--password", password,
        "--port", str(screen.port),
        "--scale", f"{screen.scale:g}",
    ]


def command_preview(screen: Screen, password: str, *, mask: bool = True) -> str:
    """给界面显示的命令行预览。默认把密码遮成 ****，避免随手截图就泄露。"""
    argv = build_argv(screen, "********" if mask else password)
    return " ".join(_shell_quote(a) for a in argv)


def _shell_quote(text: str) -> str:
    if text and all(c.isalnum() or c in "-_./=:," for c in text):
        return text
    return "'" + text.replace("'", "'\\''") + "'"


class Manager:
    """屏幕进程的增删启停与状态判定。"""

    def __init__(self, store: Store, secrets: Secrets) -> None:
        self.store = store
        self.secrets = secrets

    # --- 路径 ---------------------------------------------------------------
    def log_path(self, screen_id: str) -> Path:
        return C.LOG_DIR / f"{screen_id}.log"

    # --- 启动 ---------------------------------------------------------------
    def spawn(self, screen: Screen, password: str) -> SpawnResult:
        """启动一个虚拟屏。返回后进程已脱离本 GUI，GUI 退出不会影响它。"""
        binary = proctools.krfb_binary()
        if binary is None:
            return SpawnResult(False, error=trf(
                "krfb-virtualmonitor not found (expected at {path})", path=C.KRFB_BIN
            ))

        if password is None:
            return SpawnResult(False, error=tr("No password available"))

        # 端口冲突提前拦，比让 krfb 自己失败再解析日志可靠
        if proctools.port_in_use(screen.port):
            return SpawnResult(False, error=trf(
                "Port {port} is already in use", port=screen.port
            ))

        argv = build_argv(screen, password)
        log_file = self.log_path(screen.id)

        try:
            C.LOG_DIR.mkdir(parents=True, exist_ok=True)
            # 每次启动截断日志，避免无上限增长
            with open(log_file, "wb") as handle:
                os.chmod(log_file, 0o600)
                proc = subprocess.Popen(
                    argv,
                    stdin=subprocess.DEVNULL,
                    stdout=handle,
                    stderr=subprocess.STDOUT,
                    start_new_session=True,  # ← 约束 1 的关键：独立会话，GUI 退出不收 SIGHUP
                    close_fds=True,
                    cwd="/",                 # 不占住任何目录
                    # 必须清洗：继承 PyInstaller 注入的 LD_LIBRARY_PATH 会让 krfb
                    # 绑到包内 libQt6 上（见 envtools 的模块说明）
                    env=envtools.child_env(),
                )
        except OSError as exc:
            return SpawnResult(False, error=trf("Failed to start: {error}", error=exc))

        starttime = proctools.read_starttime(proc.pid)
        if starttime is None:
            return SpawnResult(False, pid=proc.pid,
                               error=tr("The process vanished immediately after starting"))

        # 用户主动启动 = 明确表达"我要它运行"。这个标志驱动崩溃横幅和登录自启，
        # 不设的话进程被杀掉后界面只会显示"已停止"，用户永远收不到提示。
        if not screen.desired_running:
            screen.desired_running = True
            self.store.save_screens()

        self.store.mark_started(screen.id, proc.pid, starttime)
        return SpawnResult(True, pid=proc.pid, starttime=starttime)

    # --- 停止 ---------------------------------------------------------------
    def is_recorded_process_alive(self, rt: Runtime) -> bool:
        """记录里的那个进程是否**还在跑**。

        starttime 比对是必须的：pid 会被复用，只看 pid 存在会误判，
        甚至可能把信号发给一个完全无关的进程。

        僵尸判定同样必须：进程退出后若父进程没 waitpid，/proc/<pid>/stat 还在、
        starttime 也不变 —— 光比 starttime 会把它一直当成"运行中"。而本程序正是
        这些 krfb 的父进程，实测点「停止」后进程 1 秒内退出，界面却要拖一分钟以上
        才同步（详见 proctools.read_state）。
        """
        if rt.pid is None or rt.starttime is None:
            return False
        current = proctools.read_starttime(rt.pid)
        if current is None or current != rt.starttime:
            return False
        return not proctools.is_zombie(rt.pid)

    def terminate(self, screen: Screen, *, force: bool = False, proc: ProcInfo | None = None) -> bool:
        """给虚拟屏发信号。发之前一定再核对一次身份。

        返回值只表示"信号发出去了没有"，不代表停止意图是否被记录 —— 两者分开：
        进程已经不在了（尤其是变成了僵尸：它的 /proc/<pid>/exe 读不到，身份校验
        必然失败）也要把"用户不要它跑了"记下来，否则界面会把它当成"异常退出"
        弹崩溃横幅。
        """
        rt = self.store.runtime_for(screen.id)
        pid = rt.pid
        starttime = rt.starttime

        # 未托管的进程没有 Runtime 记录，用调用方传来的 ProcInfo
        if proc is not None:
            pid, starttime = proc.pid, proc.starttime

        # 用户主动停止 = 不再期望它运行。先记意图，再做身份校验与发信号
        if screen.desired_running:
            screen.desired_running = False
            self.store.save_screens()

        if pid is None or starttime is None:
            return False

        # 双重核对：starttime 必须一致，且 exe 要是 krfb
        if proctools.read_starttime(pid) != starttime:
            return False
        exe = proctools.read_exe(pid)
        if exe is None or not proctools.looks_like_krfb(
            proctools.read_cmdline(pid) or [], exe
        ):
            return False

        try:
            os.kill(pid, signal.SIGKILL if force else signal.SIGTERM)
        except (ProcessLookupError, PermissionError):
            return False
        return True

    # --- 状态判定 -----------------------------------------------------------
    def state_of(self, screen: Screen) -> ScreenState:
        rt = self.store.runtime_for(screen.id, create=False)
        alive = self.is_recorded_process_alive(rt)

        if alive:
            return ScreenState.RUNNING

        if rt.last_error and rt.consecutive_failures > 0:
            # 上次启动就失败了，且现在没在跑
            return ScreenState.FAILED if screen.desired_running else ScreenState.STOPPED

        if screen.desired_running:
            # 期望它在跑，但它不在 —— 崩溃/被杀/机器重启过
            return ScreenState.CRASHED

        return ScreenState.STOPPED

    # --- 启动后验证 ---------------------------------------------------------
    def output_ready(self, screen: Screen) -> bool:
        """KWin 里是否已经出现 Virtual-<name> 输出。

        首选证据是 KWin 里出现 `Virtual-<name>`，这是"虚拟屏真的建成了"的唯一可靠
        证据 —— 实测 krfb 会报 portal 错误却仍然监听端口，光看进程活着会误报成功。

        但 KWin 可能**根本问不到**（kscreen-doctor 没装，或者像打包版那样一启动就
        abort，详见 envtools）。这时只能退化成"端口在监听"这个弱证据 ——
        这正是 environment_warnings 里承诺过的降级：宁可判得弱一点，也不能在虚拟屏
        明明起来了的情况下误报失败，那会让用户以为没起来、转头去折腾「扫描」纳管。
        """
        if kscreen.output_exists(screen.connector_name):
            return True
        return not kscreen.usable() and proctools.port_in_use(screen.port)

    def apply_requested_scale(self, screen: Screen) -> None:
        """把 KWin 实际生效的 scale 改成请求值，并回读真实分辨率。

        必要性：KWin 为虚拟输出持久化了一份配置，而每个新建的虚拟显示器都会拿到
        **同一个 UUID**，导致陈旧配置里的 scale 永远压过 --scale 请求值
        （实测请求 1.25 与 1.5 都变成 1.75）。建成后用 kscreen-doctor 显式设置一遍
        才能真正生效。
        """
        out = kscreen.find_output(screen.connector_name)
        if out is None:
            return

        if out.scale is not None and abs(out.scale - screen.scale) > 0.01:
            kscreen.set_scale(screen.connector_name, screen.scale)
            out = kscreen.find_output(screen.connector_name) or out

        # 回读并记录实际生效值 —— 界面必须显示这个，而不是请求值
        rt = self.store.runtime_for(screen.id)
        rt.actual_width = out.width
        rt.actual_height = out.height
        rt.actual_scale = out.scale
        self.store.save_runtimes()

    # --- 日志 ---------------------------------------------------------------
    def read_log_tail(self, screen_id: str, max_bytes: int = 8192) -> str:
        path = self.log_path(screen_id)
        try:
            size = path.stat().st_size
            with open(path, "rb") as handle:
                if size > max_bytes:
                    handle.seek(size - max_bytes)
                data = handle.read()
        except OSError:
            return ""
        return data.decode("utf-8", "replace")

    # --- 认领外部进程 -------------------------------------------------------
    def unmanaged_processes(self) -> list[ProcInfo]:
        """扫描 /proc，找出属于本用户、但不在 store 里的 krfb 进程。

        proctools 已经按 uid 过滤并跳过空 cmdline —— 否则会列出*其他用户*的
        krfb 实例并提议去杀它们。
        """
        known: set[tuple[int, int | None]] = set()
        for screen in self.store.screens.values():
            rt = self.store.runtime_for(screen.id, create=False)
            if rt.pid is not None:
                known.add((rt.pid, rt.starttime))

        result: list[ProcInfo] = []
        for info in proctools.iter_krfb_processes():
            if (info.pid, info.starttime) in known:
                continue
            # 参数不全的进程（比如缺少 --name/--port）无法纳管，不列出
            if info.name is None or info.port is None:
                continue
            result.append(info)
        return result

    def adopt(self, info: ProcInfo) -> tuple[Screen | None, str]:
        """把一个外部启动的进程纳入管理。返回 (屏幕, 错误信息)。"""
        assert info.name is not None and info.port is not None

        if self.store.name_taken(info.name):
            return None, trf('The name "{name}" is already taken by a managed screen',
                             name=info.name)
        if self.store.port_taken(info.port):
            return None, trf("Port {port} is already taken by a managed screen",
                             port=info.port)

        width, height = C.DEFAULT_RESOLUTION
        if info.resolution and "x" in info.resolution:
            left, _, right = info.resolution.partition("x")
            if left.isdigit() and right.isdigit():
                width, height = int(left), int(right)

        screen = Screen(
            name=info.name,
            width=width,
            height=height,
            scale=info.scale or C.DEFAULT_SCALE,
            port=info.port,
            # 用户可编辑的备注：写盘即冻结在当时的语言（事件记录，不该再翻译）
            notes=tr("Imported from an externally started process"),
            desired_running=True,  # 它正在跑，用户的意图显然是"要它运行"
        )
        self.store.add(screen)
        self.store.mark_started(screen.id, info.pid, info.starttime)

        # 密码可以从 /proc/<pid>/cmdline 里读出来（同用户可读），直接接管，
        # 用户手敲的那条命令立刻变成完全可管理的虚拟屏
        if info.password:
            self.secrets.set(screen.id, info.password)

        self.apply_requested_scale(screen)
        return screen, ""

    # --- 环境自检 -----------------------------------------------------------
    def environment_warnings(self) -> list[str]:
        """启动时做一次环境自检，把会破坏核心需求的情况显式暴露出来。"""
        warnings: list[str] = []

        if proctools.krfb_binary() is None:
            warnings.append(trf(
                "krfb-virtualmonitor not found; make sure krfb is installed "
                "(expected at {path}).", path=C.KRFB_BIN,
            ))

        wayland = wayland_problem()
        if wayland:
            warnings.append(wayland)

        if not kscreen.available():
            warnings.append(tr(
                "kscreen-doctor not found, so the real resolution and scale of a "
                "virtual screen can't be read back; startup verification falls "
                "back to checking the port only."
            ))
        elif not kscreen.usable():
            # 二进制在、但问不到 KWin（打包版里被包内 Qt6 污染后正是如此）。
            # 只说"找不到"会漏掉这种情况，界面上会显示成一片正常的假全绿。
            warnings.append(tr(
                "kscreen-doctor exists but returns no output (the packaged build "
                "was once poisoned by its bundled Qt6 and aborted), so the real "
                "resolution and scale of a virtual screen can't be read back; "
                "startup verification falls back to checking the port only."
            ))

        cgroup = cgroup_risk()
        if cgroup:
            warnings.append(cgroup)

        return warnings


def wayland_problem() -> str | None:
    """虚拟显示器**只能**在 Wayland 下工作，且 socket 必须可达。

    实测：一旦 `WAYLAND_DISPLAY` 指向不存在的 socket（例如 XDG_RUNTIME_DIR 被改过），
    krfb 只会打印 "Failed to create wl_display" 和
    "Virtual Monitors are only supported on Wayland" 然后退出。
    这类失败在界面上很难自解释，所以提前查、明确说。
    """
    display = os.environ.get("WAYLAND_DISPLAY")
    if not display:
        if os.environ.get("XDG_SESSION_TYPE") == "wayland":
            # 是 Wayland 会话但没拿到 socket 名，通常是从缺环境变量的服务里启动的
            return tr(
                "This is a Wayland session but WAYLAND_DISPLAY is not set, so "
                "krfb cannot create virtual monitors. Start this program from the "
                "desktop launcher or a terminal."
            )
        return tr(
            "This is not a Wayland session. krfb's virtual monitors require "
            "Wayland (and KWin); under X11 they fail outright."
        )

    path = Path(display) if display.startswith("/") else Path(
        os.environ.get("XDG_RUNTIME_DIR") or "/run/user/0"
    ) / display
    if not path.exists():
        # 引号里的是 krfb 的原样输出，必须保持英文，方便用户拿去搜日志
        return trf(
            "WAYLAND_DISPLAY={display} points to a socket that does not exist "
            "({path}); krfb will fail with "
            "\"Virtual Monitors are only supported on Wayland\".",
            display=display, path=path,
        )
    return None


def cgroup_risk() -> str | None:
    """检测父 systemd unit 是否会在 GUI 退出时连带杀掉所有虚拟屏。

    背景：`setsid()` 能防 SIGHUP，防不住 cgroup 级的清理。若父 unit 是
    `KillMode=control-group` + `ExitType=main`，GUI 主进程一退出，systemd 就会
    SIGTERM 整个 cgroup —— 所有虚拟屏陪葬。`ExitType=cgroup` 则安全（unit 会等到
    最后一个进程退出）。

    本机实测是 `ExitType=cgroup`，安全；但这条检查很便宜，而它保护的正是本工程的
    头号需求。
    """
    try:
        text = Path("/proc/self/cgroup").read_text(encoding="utf-8").strip()
    except OSError:
        return None

    path = text.rsplit(":", 1)[-1] if ":" in text else text
    if not path.endswith(".service"):
        return None  # 不在 systemd unit 里（比如从终端直接跑），没有这个风险
    unit = path.rsplit("/", 1)[-1]

    # 同样要走清洗过的环境：包里带着 libcrypto.so.3 / libssl.so.3，
    # 系统工具 dlopen 到它就可能因为版本不匹配出问题。
    proc = envtools.run_helper(
        ["systemctl", "--user", "show", unit, "-p", "KillMode", "-p", "ExitType"],
        timeout=3,
    )
    if proc is None:
        return None

    props = dict(
        line.split("=", 1) for line in proc.stdout.splitlines() if "=" in line
    )
    if props.get("KillMode") == "control-group" and props.get("ExitType") == "main":
        return trf(
            "Started by systemd unit {unit}, whose KillMode=control-group and "
            "ExitType=main mean that quitting this program kills every virtual "
            "screen along with it. Run it from the desktop launcher instead, or "
            "add ExitType=cgroup to that unit.", unit=unit,
        )
    return None


def now() -> float:
    return time.time()
