"""纯 /proc 读取工具。无状态、不依赖 Qt，可以单独测试。

设计要点：
  * 身份用 (name, port)，存活用 pidfd + starttime —— 两者职责不混。
  * 扫描进程时必须按 uid 过滤，否则会列出*其他用户*的 krfb 并提议杀掉它们。
  * 必须跳过空 cmdline（僵尸进程与内核线程没有 cmdline），否则解析器会炸。
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from .constants import KRFB_BIN
from .models import ProcInfo

# 从 /proc/<pid>/stat 里取 starttime。comm 字段（第 2 个）可能含空格和括号，
# 所以必须从**最后一个**右括号之后再切分，不能简单 split()。
_STAT_FIELDS_AFTER_COMM = 3  # 右括号之后第一个字段是 state，即第 3 个字段
_STARTTIME_FIELD = 22


def read_text(path: str | Path) -> str | None:
    try:
        return Path(path).read_text(errors="replace")
    except (OSError, UnicodeError):
        return None


def read_cmdline(pid: int) -> list[str] | None:
    """读取并切分 /proc/<pid>/cmdline。空文件（僵尸/内核线程）返回 None。"""
    try:
        raw = Path(f"/proc/{pid}/cmdline").read_bytes()
    except OSError:
        return None
    if not raw:
        return None
    return raw.decode("utf-8", "replace").rstrip("\0").split("\0")


def read_starttime(pid: int) -> int | None:
    """读取进程启动时刻（内核 jiffies）。这是防 PID 复用的关键字段。"""
    data = read_text(f"/proc/{pid}/stat")
    if data is None:
        return None
    rparen = data.rfind(")")
    if rparen < 0:
        return None
    fields = data[rparen + 1 :].split()
    idx = _STARTTIME_FIELD - _STAT_FIELDS_AFTER_COMM
    if idx >= len(fields):
        return None
    try:
        return int(fields[idx])
    except ValueError:
        return None


def read_exe(pid: int) -> str | None:
    """读 /proc/<pid>/exe 的软链接目标。

    这是比 argv[0] 更可靠的身份判据：`exec -a` 可以伪造 argv[0]，但伪造不了 exe。
    """
    try:
        return os.readlink(f"/proc/{pid}/exe")
    except OSError:
        return None


def read_state(pid: int) -> str | None:
    """读 /proc/<pid>/stat 的状态字符：R/S/D/Z/T…

    存在的唯一理由是**僵尸**：进程退出后，若父进程没有 `waitpid`，它不会消失 ——
    `/proc/<pid>/stat` 还在，starttime 也不变，于是"正在运行"和"早已死透但还没被
    回收"在读 /proc 时长得一模一样。

    本程序正好是这些 krfb 的父进程，于是必踩：点「停止」后进程 1 秒内就退出
    （KWin 也把虚拟屏摘了），但界面上它仍是"运行中"，直到某个偶然事件触发 Python
    回收子进程（`subprocess` 只在下一次创建 Popen 时才顺手 `_cleanup()`）为止 ——
    实测能拖到一分钟以上。
    """
    data = read_text(f"/proc/{pid}/stat")
    if data is None:
        return None
    rparen = data.rfind(")")
    if rparen < 0:
        return None
    fields = data[rparen + 1:].split()
    return fields[0] if fields else None


def is_zombie(pid: int) -> bool:
    """进程是否已经退出、只是在等父进程回收。

    它**不占端口、不占内存**，但 PID 还没释放 —— 所以既不是"活着"，也不能按
    "PID 可能被复用"来防备（内核会一直留着这个号直到被回收）。
    """
    return read_state(pid) == "Z"


def pid_alive(pid: int) -> bool:
    """进程是否**真的还在跑**（僵尸不算）。

    "还在跑"的主判据始终是 `read_starttime` 比对（防 PID 复用），这个函数只是个
    廉价的粗筛。目前没有调用方 —— 留着是因为它的字面意思容易被将来的代码误用，
    索性让这个名字名副其实。
    """
    return Path(f"/proc/{pid}").exists() and not is_zombie(pid)


def is_our_uid(pid: int) -> bool:
    """进程是否属于当前用户。/proc/<pid>/cmdline 是 0444，任何人都能读，
    不过滤的话扫描结果里会混进别人的 krfb 实例。"""
    try:
        return os.stat(f"/proc/{pid}").st_uid == os.getuid()
    except OSError:
        return False


def looks_like_krfb(argv: list[str], exe: str | None) -> bool:
    if exe is not None:
        base = os.path.basename(exe.removesuffix(" (deleted)"))
        if base == "krfb-virtualmonitor":
            return True
    if argv:
        return os.path.basename(argv[0]) == "krfb-virtualmonitor"
    return False


def parse_krfb_argv(argv: list[str]) -> dict[str, str]:
    """把 krfb-virtualmonitor 的参数解析成 {选项名: 值}。

    Qt 的 QCommandLineParser 同时接受 `--name Foo` 和 `--name=Foo`，两种都要认。
    """
    out: dict[str, str] = {}
    i = 1
    while i < len(argv):
        arg = argv[i]
        if not arg.startswith("--"):
            i += 1
            continue
        body = arg[2:]
        if "=" in body:
            key, value = body.split("=", 1)
            out[key] = value
        elif i + 1 < len(argv):
            out[body] = argv[i + 1]
            i += 1
        i += 1
    return out


def _parse_resolution(text: str | None) -> tuple[int, int] | None:
    if not text or "x" not in text:
        return None
    left, _, right = text.partition("x")
    try:
        return int(left), int(right)
    except ValueError:
        return None


def describe_process(pid: int) -> ProcInfo | None:
    """把单个 pid 读成 ProcInfo；不是 krfb 进程或读不到就返回 None。"""
    argv = read_cmdline(pid)
    exe = read_exe(pid)
    if argv is None or not looks_like_krfb(argv, exe):
        return None
    starttime = read_starttime(pid)
    if starttime is None:
        return None

    opts = parse_krfb_argv(argv)
    res = _parse_resolution(opts.get("resolution"))
    port = opts.get("port")
    scale = opts.get("scale")

    return ProcInfo(
        pid=pid,
        starttime=starttime,
        exe=exe or "",
        argv=tuple(argv),
        name=opts.get("name"),
        port=int(port) if port and port.isdigit() else None,
        resolution=f"{res[0]}x{res[1]}" if res else None,
        scale=float(scale) if scale and _is_float(scale) else None,
        password=opts.get("password"),
    )


def _is_float(text: str) -> bool:
    try:
        float(text)
        return True
    except ValueError:
        return False


def iter_krfb_processes() -> list[ProcInfo]:
    """扫描 /proc，列出当前用户的所有 krfb-virtualmonitor 进程。"""
    found: list[ProcInfo] = []
    try:
        entries = os.listdir("/proc")
    except OSError:
        return found

    for entry in entries:
        if not entry.isdigit():
            continue
        pid = int(entry)
        if not is_our_uid(pid):
            continue  # 别人的进程，跟我们无关
        info = describe_process(pid)
        if info is not None:
            found.append(info)
    found.sort(key=lambda p: p.pid)
    return found


def listening_ports() -> set[int]:
    """解析 /proc/net/tcp{,6}，返回所有处于 LISTEN 状态的本地端口。

    st 字段为 '0A' 表示 LISTEN。纯 Python 解析，不需要 ss/netstat，也不需要 root。
    """
    ports: set[int] = set()
    for name in ("/proc/net/tcp", "/proc/net/tcp6"):
        data = read_text(name)
        if data is None:
            continue
        for line in data.splitlines()[1:]:  # 跳过表头
            fields = line.split()
            if len(fields) < 4 or fields[3] != "0A":
                continue
            _, _, port_hex = fields[1].rpartition(":")
            try:
                ports.add(int(port_hex, 16))
            except ValueError:
                continue
    return ports


def port_in_use(port: int) -> bool:
    return port in listening_ports()


def krfb_binary() -> str | None:
    """定位 krfb-virtualmonitor。优先用绝对路径常量，退回 PATH 查找。"""
    if Path(KRFB_BIN).exists():
        return KRFB_BIN
    return shutil.which("krfb-virtualmonitor")
