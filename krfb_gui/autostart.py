"""开机自启：单个应用级 .desktop，而不是每个虚拟屏一个。

为什么不做"每个屏幕一个 .desktop"：那需要把 `--password` 明文写进 0644 的桌面
文件里，比专门用密钥环加密存储还退步 —— 等于白做加密。

改为启动 GUI 自身（托盘模式，不弹窗），由 GUI 从密钥环取密码后拉起所有
`desired_running` 的屏幕。密码始终不经手磁盘明文。

附带好处：KDE 的 systemd-xdg-autostart-generator 生成的单元恰好是
`ExitType=cgroup`（配合 manager.cgroup_risk 的检查是安全的），且
`PartOf=graphical-session.target`，登出即停 —— 符合预期，因为虚拟显示器本来
就随 KWin 一起消失。
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from . import constants as C
from .i18n import LANGUAGES, for_lang, trf

# .desktop 的 Comment 英文原文（i18n 的 key）。Name 用 C.APP_NAME。
_DESKTOP_COMMENT = 'Restore virtual screens marked as "desired running" at login'


def _project_root() -> Path:
    # autostart.py 在 <root>/krfb_gui/ 下
    return Path(__file__).resolve().parent.parent


def _entry_path() -> Path:
    return C.AUTOSTART_FILE


def _quote(value: str) -> str:
    """Desktop Entry 规范的引用方式：含空格等字符时用双引号包裹。"""
    if value and all(c.isalnum() or c in "-_./=:," for c in value):
        return value
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def launcher_command() -> list[str]:
    """构造自启时执行的命令。

    打包后（PyInstaller）`sys.executable` 就是那个独立可执行程序本身，包内没有
    可执行的 main.py 可跑，只能让它自己带 --tray 重启。源码运行时才是
    「当前解释器 + main.py」。
    """
    if getattr(sys, "frozen", False):
        return [sys.executable, "--tray"]
    return [sys.executable, str(_project_root() / "main.py"), "--tray"]


def is_enabled() -> bool:
    return _entry_path().exists()


def _localized_lines(prefix: str, english: str) -> str:
    """一组 `Name=` / `Name[xx]=` 行。

    默认键按 Desktop Entry 规范用英文（区域不在表里的按英文显示），其余每种
    受支持语言各写一行。文件内容与界面的语言偏好无关（切换语言不重写它），
    菜单里显示哪种由桌面环境按系统区域自己挑。
    """
    lines = [f"{prefix}={_quote(english)}"]
    for lang in LANGUAGES:
        if lang == "en":
            continue
        lines.append(f"{prefix}[{lang}]={_quote(for_lang(lang, english))}")
    return "\n".join(lines) + "\n"


def enable() -> tuple[bool, str]:
    """写入自启项。返回 (是否成功, 错误信息)。"""
    path = _entry_path()
    command = " ".join(_quote(part) for part in launcher_command())
    content = (
        "[Desktop Entry]\n"
        "Type=Application\n"
        f"{_localized_lines('Name', C.APP_NAME)}"
        f"{_localized_lines('Comment', _DESKTOP_COMMENT)}"
        f"Exec={command}\n"
        "Icon=krfb\n"
        "Terminal=false\n"
        "StartupNotify=false\n"
        "X-GNOME-Autostart-enabled=true\n"
        # KDE：等面板起来之后再启动，避免抢在托盘可用之前
        "X-KDE-autostart-after=panel\n"
    )
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        os.chmod(path, 0o644)  # 里面没有秘密，可读无妨
    except OSError as exc:
        return False, trf("Cannot write {path}: {error}", path=path, error=exc)
    return True, ""


def disable() -> tuple[bool, str]:
    path = _entry_path()
    try:
        path.unlink(missing_ok=True)
    except OSError as exc:
        return False, trf("Cannot delete {path}: {error}", path=path, error=exc)
    return True, ""


def set_enabled(enabled: bool) -> tuple[bool, str]:
    return enable() if enabled else disable()
