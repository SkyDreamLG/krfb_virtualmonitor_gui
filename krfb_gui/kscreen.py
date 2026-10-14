"""回读 KWin/KScreen 的真实输出状态。

为什么需要这个模块：`--scale` 参数**不可信**。实测在 KWin 下：

    请求 --scale 1.25  →  Modes: 38:2560x1600@60.00*!   Geometry: 0,0 1463x915   Scale: 1.75
    请求 --scale 1.5   →                                实际 1.75

原因是 KWin 在 kwinoutputconfig.json 里为虚拟输出持久化了一份配置，而**每个新建的
虚拟显示器都会拿到同一个 UUID**（实测 Virtual-Probe 与 Virtual-FmtProbe 的 UUID 都是
27e99bcc-…），于是那份陈旧配置里的 scale 永远压过命令行请求值。

所以：
  1. "虚拟屏真的建成了"的唯一可靠证据是 KWin 里出现 `Virtual-<name>` 输出；
  2. 界面上必须显示回读值而不是请求值；
  3. 想让 scale 生效，只能建成之后再用 kscreen-doctor 显式设置一遍（实测有效）。
"""

from __future__ import annotations

import re
import shutil

from . import envtools

_ANSI = re.compile(r"\x1b\[[0-9;]*m")
_OUTPUT_HEAD = re.compile(r"^Output:\s+(\d+)\s+(\S+)\s+(\S+)\s*$")
_GEOMETRY = re.compile(r"^\s*Geometry:\s*(-?\d+),(-?\d+)\s+(\d+)x(\d+)\s*$")
_SCALE = re.compile(r"^\s*Scale:\s*([\d.]+)\s*$")
_MODE = re.compile(r"(\d+)x(\d+)@[\d.]+(\*?)")

KSCREEN_DOCTOR = "kscreen-doctor"


def available() -> bool:
    return shutil.which(KSCREEN_DOCTOR) is not None


def usable() -> bool:
    """kscreen-doctor 是否**真的**问得到 KWin —— 不只是"PATH 里有这个文件"。

    `available()` 只查 PATH，答不上"二进制在、一启动就崩"这种情况：打包版里
    kscreen-doctor 继承了 PyInstaller 注入的 `LD_LIBRARY_PATH`，去加载包内 Qt6 后
    找不到平台插件直接 abort（详见 envtools 的模块说明）。所以这里实跑一次 `-o`
    看有没有结果 —— 正是这个失败让启动校验误报超时的。

    不缓存：本函数只在正常回读拿不到输出之后才被调用，正常机器一次都不会走到；
    每个 2 秒轮询多一次子进程调用，换来的是"KWin 恢复后立刻回到严格判定"。
    崩掉和"屏幕真的一个都没有"都归为 False（两者都意味着我们问不到 KWin）。
    """
    return available() and bool(list_outputs())


def _run(args: list[str], timeout: float = 4.0) -> str | None:
    # 环境必须清洗：打包版会把 LD_LIBRARY_PATH 指向包内 Qt6，继承过去
    # kscreen-doctor 会加载到错误的 libQt6、找不到平台插件而直接 abort
    # （实测 exit 134、stdout 全空），于是 list_outputs() 永远返回空。
    proc = envtools.run_helper([KSCREEN_DOCTOR, *args], timeout=timeout)
    if proc is None:
        return None
    return _ANSI.sub("", proc.stdout)


class Output:
    """一个 KWin 输出（显示器）的当前状态。"""

    __slots__ = ("index", "connector", "uuid", "enabled", "width", "height", "scale", "logical_width", "logical_height")

    def __init__(self, index: int, connector: str, uuid: str) -> None:
        self.index = index
        self.connector = connector
        self.uuid = uuid
        self.enabled = False
        # width/height 是当前 mode 的物理分辨率（即 --resolution 请求的那个值）
        self.width: int | None = None
        self.height: int | None = None
        # scale 是 KWin 实际生效的缩放，可能不等于请求值
        self.scale: float | None = None
        # logical_* 是缩放后的逻辑尺寸（Geometry 里的 WxH）
        self.logical_width: int | None = None
        self.logical_height: int | None = None

    @property
    def is_virtual(self) -> bool:
        return self.connector.startswith("Virtual-")

    def __repr__(self) -> str:  # pragma: no cover - 调试用
        return (
            f"<Output {self.connector} {self.width}x{self.height}@{self.scale} "
            f"logical={self.logical_width}x{self.logical_height}>"
        )


def list_outputs() -> list[Output]:
    """解析 `kscreen-doctor -o`。解析不出来就返回空列表，不抛异常。

    注意：kscreen-doctor 会输出 ANSI 颜色转义（颜色码甚至嵌在 Modes 行中间），
    必须先剥掉再解析。
    """
    text = _run(["-o"])
    if text is None:
        return []

    outputs: list[Output] = []
    current: Output | None = None

    for raw_line in text.splitlines():
        head = _OUTPUT_HEAD.match(raw_line)
        if head:
            current = Output(int(head.group(1)), head.group(2), head.group(3))
            outputs.append(current)
            continue
        if current is None:
            continue

        stripped = raw_line.strip()

        if stripped == "enabled":
            current.enabled = True
        elif stripped.startswith("Modes:"):
            # 带 '*' 的那个是当前 mode，其尺寸就是物理分辨率
            for match in _MODE.finditer(stripped):
                if match.group(3) == "*":
                    current.width = int(match.group(1))
                    current.height = int(match.group(2))
                    break
        else:
            geom = _GEOMETRY.match(raw_line)
            if geom:
                current.logical_width = int(geom.group(3))
                current.logical_height = int(geom.group(4))
                continue
            scale = _SCALE.match(raw_line)
            if scale:
                try:
                    current.scale = float(scale.group(1))
                except ValueError:
                    pass

    return outputs


def find_output(connector: str) -> Output | None:
    for out in list_outputs():
        if out.connector == connector:
            return out
    return None


def output_exists(connector: str) -> bool:
    """虚拟屏是否真的建立起来了。这比"进程还活着"可信得多。"""
    return find_output(connector) is not None


def set_scale(connector: str, scale: float) -> bool:
    """用 kscreen-doctor 把缩放改成请求值。

    这是绕开"kwinoutputconfig.json 陈旧配置压过 --scale"的唯一干净办法：
    先让 krfb 建好输出，再显式设置一次。实测有效。
    """
    if not available():
        return False
    # 用 output.<连接器名>.scale.<值> 的语法，比索引更稳（索引会随输出增删变化）
    _run([f"output.{connector}.scale.{scale}"])
    out = find_output(connector)
    return out is not None and out.scale is not None and abs(out.scale - scale) < 0.01
