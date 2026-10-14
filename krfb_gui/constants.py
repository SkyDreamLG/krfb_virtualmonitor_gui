"""全局常量：XDG 路径、krfb 参数约束、子进程环境变量白名单。

这里集中所有"魔法值"，其余模块只引用不重复定义。
"""

from __future__ import annotations

import os
from pathlib import Path

APP_ID = "krfb-virtualmonitor-gui"
# 界面文案的英文原文即 i18n 的 key。这里不能 import i18n（i18n 要 import 本模块
# 取 SETTINGS_FILE，会成环），所以显示处一律写 tr(C.APP_NAME)。
APP_NAME = "Krfb Virtual Screen Manager"
APP_VERSION = "0.1.0"

# krfb-virtualmonitor 的可执行文件。用绝对路径，避免依赖子进程继承的 PATH。
KRFB_BIN = "/usr/bin/krfb-virtualmonitor"


def _xdg(env_var: str, fallback: str) -> Path:
    """按 XDG 规范解析目录：环境变量非空则用它，否则用 ~/<fallback>。"""
    value = os.environ.get(env_var)
    return Path(value) if value else Path.home() / fallback


# --- 存储布局 ---------------------------------------------------------------
# 配置（用户意图，变化少）与运行态（进程 pid/实测值，变化频繁）分开存放，
# 避免每次进程事件都重写配置文件，也避免两个实例互相覆盖更新。
CONFIG_DIR = _xdg("XDG_CONFIG_HOME", ".config") / APP_ID
STATE_DIR = _xdg("XDG_STATE_HOME", ".local/state") / APP_ID
RUNTIME_DIR = Path(os.environ.get("XDG_RUNTIME_DIR") or f"/tmp/{APP_ID}")

SCREENS_FILE = CONFIG_DIR / "screens.json"
RUNTIME_FILE = STATE_DIR / "runtime.json"
# 界面偏好（目前只有语言）。i18n 模块自己读写这个文件 —— 它不能 import store。
SETTINGS_FILE = CONFIG_DIR / "settings.json"
LOG_DIR = STATE_DIR / "logs"
LOCK_FILE = RUNTIME_DIR / f"{APP_ID}.lock"
AUTOSTART_FILE = _xdg("XDG_CONFIG_HOME", ".config") / "autostart" / f"{APP_ID}.desktop"

# --- krfb 参数约束 ----------------------------------------------------------
PORT_MIN, PORT_MAX = 5900, 5999
DEFAULT_PORT = 5900
DEFAULT_RESOLUTION = (2736, 1824)  # 用户当前的主力平板分辨率
DEFAULT_SCALE = 1.0
SCALE_MIN, SCALE_MAX = 0.5, 4.0

RESOLUTION_MIN, RESOLUTION_MAX = 320, 16384

# VNC 的 DES 认证只使用密码的前 8 个字符，更长的密码不会增加任何熵。
# 所以生成器只生成 8 位，UI 也要如实说明。
VNC_PASSWORD_LEN = 8
# 去掉了 0/O/1/l/I 等易混字符，方便用户手抄。
PASSWORD_ALPHABET = "abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789"

# (宽, 高, 说明)，覆盖常见笔记本/平板/显示器
RESOLUTION_PRESETS: tuple[tuple[int, int, str], ...] = (
    (1280, 720, "720p"),
    (1920, 1080, "1080p 16:9"),
    (1920, 1200, "WUXGA 16:10"),
    (2560, 1440, "1440p 16:9"),
    (2560, 1600, "WQXGA 16:10"),
    (2736, 1824, "3:2 Tablet"),
    (2880, 1800, "MacBook 15\" 16:10"),
    (3000, 2000, "Surface Book 3:2"),
    (3840, 2160, "4K 16:9"),
)

# --- 子进程环境变量白名单 ----------------------------------------------------
# 用户 shell 里导出了 ROS/CUDA 的 LD_LIBRARY_PATH 与 PYTHONPATH。krfb-virtualmonitor
# 是 Qt6 C++ 程序，继承这些变量会绑错 libQt6；PYTHONPATH 也会污染子进程。
# 因此只透传"运行桌面程序必需"的变量，其余一律丢弃。
ENV_PASSTHROUGH = frozenset(
    {
        "PATH",
        "HOME",
        "USER",
        "LOGNAME",
        "SHELL",
        "LANG",
        "LC_ALL",
        "LC_CTYPE",
        "XDG_RUNTIME_DIR",
        "XDG_SESSION_TYPE",
        "XDG_SESSION_ID",
        "XDG_CURRENT_DESKTOP",
        "XDG_SESSION_DESKTOP",
        "XDG_DATA_HOME",
        "XDG_CONFIG_HOME",
        "XDG_STATE_HOME",
        "XDG_CACHE_HOME",
        "XDG_DATA_DIRS",
        "XDG_CONFIG_DIRS",
        "WAYLAND_DISPLAY",
        "WAYLAND_SOCKET",
        "DISPLAY",
        "DBUS_SESSION_BUS_ADDRESS",
        "XAUTHORITY",
    }
)

# 前缀匹配的黑名单：即使将来白名单不慎放宽，这几个前缀也永远不传给子进程。
ENV_DENY_PREFIXES = ("LD_", "QT_", "GTK_", "GDK_", "PYTHON", "VIRTUAL_ENV")

# --- 界面 -------------------------------------------------------------------
SIDEBAR_WIDTH = 232
DETAIL_MIN_WIDTH = 420
WINDOW_DEFAULT_SIZE = (980, 660)
WINDOW_MIN_SIZE = (760, 520)

# 状态轮询间隔（毫秒）。进程存活走 pidfd 事件通知，这个只用于兜底与实测值刷新。
POLL_INTERVAL_MS = 2000
# 启动后等待 KWin 出现 Virtual-<name> 输出的上限
SPAWN_VERIFY_TIMEOUT_MS = 8000
# 密钥环调用在 UI 侧的容忍上限，超过就降级，绝不阻塞主线程
KEYRING_TIMEOUT_MS = 2000

SERVICE_NAME = APP_ID  # keyring 的 service 名，username 用 screen.id
