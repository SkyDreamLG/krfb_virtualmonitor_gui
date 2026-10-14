"""子进程环境清洗：所有外部命令都必须经由这里启动。

为什么要有这么一个模块：

  * **打包版会毒化环境。** PyInstaller 的 Linux 启动器会往 GUI *自己*的环境里注入
    `LD_LIBRARY_PATH=<包内 _internal>:<原值>`（原值另存为 `LD_LIBRARY_PATH_ORIG`），
    好让 GUI 加载包内的 Qt6。这个变量会**继承给每一个子进程**，而本程序要调用的
    全是系统 Qt 程序：

        $ LD_LIBRARY_PATH=dist/krfb-virtualmonitor-gui/_internal kscreen-doctor -o
        qt.qpa.plugin: Could not find the Qt platform plugin "wayland" in ""
        → exit 134（SIGABRT），stdout 全空

    后果不是"少个提示"：`kscreen.list_outputs()` 永远返回空 → 启动成功判定永久
    失败 → 8 秒后误报超时。所以凡是起子进程的地方都必须走这里。

  * **必须独立成模块。** `manager.py` 要 import `kscreen.py`（回读输出），所以
    `kscreen.py` 不能反过来 import `manager` —— 否则循环导入。而环境策略必须两边
    共用，否则就会变成"krfb 子进程干净、kscreen-doctor 被污染"这种半吊子状态。

本模块只依赖 os / subprocess / constants，不 import Qt，可以单独测试。
"""

from __future__ import annotations

import os
import subprocess

from . import constants as C


def child_env() -> dict[str, str]:
    """构造给子进程的环境变量：只透传白名单里的变量。

    用户的 shell 里导出了 ROS 的 `LD_LIBRARY_PATH=/opt/ros/...` 和 `PYTHONPATH=...`，
    打包后 PyInstaller 又往 `LD_LIBRARY_PATH` 前面插了包内的 `_internal` ——
    两者对系统 Qt 程序都是致命的，必须在子进程里剥掉。剥掉 `QT_*` 还有个副作用
    好处：GUI 自己用 offscreen 平台做测试时，子进程不会跟着被污染。

    白名单里那几个 `XDG_*` / `WAYLAND_DISPLAY` / `DBUS_SESSION_BUS_ADDRESS` 缺一
    不可：实测给 kscreen-doctor 一个只有 PATH 的环境，它就连不上 Wayland 直接 abort。

    每次调用重新构造（几十次字典写入，微秒级），不做缓存 —— 不在"环境变了但
    缓存没变"上留坑。
    """
    env: dict[str, str] = {}
    for key, value in os.environ.items():
        if key not in C.ENV_PASSTHROUGH:
            continue
        if any(key.startswith(prefix) for prefix in C.ENV_DENY_PREFIXES):
            continue
        env[key] = value

    # PATH 本身也在白名单里，这里只在用户环境连 PATH 都没设时才兜底。
    env.setdefault("PATH", "/usr/local/bin:/usr/bin:/bin")
    return env


def run_helper(argv: list[str], *, timeout: float) -> subprocess.CompletedProcess[str] | None:
    """用清洗过的环境跑一个外部命令；起不来或超时返回 None。

    统一入口的意义：外部命令只要都从这里走，就不可能有哪一个漏掉 `env=`。
    `tests/test_child_env.py` 里有一条静态规则在守这件事（它会扫出任何裸的
    `subprocess.*` 调用）。

    返回值语义与 `subprocess.run(check=False)` 一致，调用方自己看 returncode/stdout。
    """
    try:
        return subprocess.run(
            argv,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            env=child_env(),
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
