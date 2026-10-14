"""界面偏好（settings.json）：语言、关闭窗口时的行为。

与 store.py 的分工：store 管**虚拟屏**的配置与运行态，这里管**界面自己**的偏好。
两者都做原子写，但刻意不共用代码 —— i18n 要用本模块，而 i18n 绝不 import store
（store 反过来要用 i18n 翻译报错文案，会成环）。

读取永不抛异常、永不建目录（测试脚本会把配置指到临时目录，那里可能压根没有这个
文件）；写失败只返回错误，由调用方决定是否提示。
"""

from __future__ import annotations

import contextlib
import json
import os
import tempfile
from pathlib import Path

from . import constants as C

SCHEMA_VERSION = 1

# 键 → 默认值。只认这几个键，别的数据一律不往偏好文件里写。
DEFAULTS: dict[str, str] = {
    "language": "system",     # system / zh_CN / zh_TW / ja / ...（见 i18n.LANGUAGES）
    "close_action": "ask",    # 点窗口关闭按钮时的行为，取值见下面三个常量
}

# close_action 的三个取值
CLOSE_ASK = "ask"    # 每次都问
CLOSE_TRAY = "tray"  # 最小化到托盘
CLOSE_QUIT = "quit"  # 退出程序
CLOSE_ACTIONS: tuple[str, ...] = (CLOSE_ASK, CLOSE_TRAY, CLOSE_QUIT)

_cache: dict[str, str] | None = None


# --- 读写 --------------------------------------------------------------------
def get(key: str, default: str | None = None) -> str:
    """读一个偏好。键不认识时返回 default（再退回 DEFAULTS 里的默认值）。"""
    values = _load()
    if key in values:
        return values[key]
    return DEFAULTS.get(key, default if default is not None else "")


def set_value(key: str, value: str) -> tuple[bool, str]:
    """写一个偏好，返回 (是否写盘成功, 错误信息)。

    名字不叫 set 是为了不遮蔽内建函数；写盘失败**不会**回滚内存里的值 ——
    用户的选择在本次会话内照常生效，与 secrets / i18n 的降级哲学一致。
    """
    if key not in DEFAULTS:
        # 开发者错误，面向代码而不是用户
        return False, f"unknown preference key: {key!r}"
    values = _load()
    values[key] = value
    return _write(values)


def reload() -> None:
    """丢掉缓存、重读文件（测试用；正常路径靠 set_value）。"""
    global _cache
    _cache = None


# --- 关闭行为 ---------------------------------------------------------------
def close_action() -> str:
    """点关闭按钮时的行为。文件里是垃圾值一律当"每次询问"。"""
    value = get("close_action")
    return value if value in CLOSE_ACTIONS else CLOSE_ASK


def set_close_action(action: str) -> tuple[bool, str]:
    if action not in CLOSE_ACTIONS:
        action = CLOSE_ASK
    return set_value("close_action", action)


# --- 内部 --------------------------------------------------------------------
def _path() -> Path:
    # 调用时取属性而不是 from ... import：测试改 C.SETTINGS_FILE 才能生效，
    # 也保证 import 期不碰用户目录。
    return C.SETTINGS_FILE


def _load() -> dict[str, str]:
    global _cache
    if _cache is not None:
        return _cache

    values = dict(DEFAULTS)
    try:
        raw = json.loads(_path().read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeError):
        # 文件缺失（首次运行）、权限不足、JSON 坏 —— 一律当"没写过"。
        raw = None
    if isinstance(raw, dict):
        for key in DEFAULTS:
            value = raw.get(key)
            if isinstance(value, str):
                values[key] = value
    _cache = values
    return _cache


def _write(values: dict[str, str]) -> tuple[bool, str]:
    """原子写（临时文件 → rename），见 store.atomic_write_json。

    这里不 fsync 父目录：偏好丢了最坏只是回到默认值，不值得为它加一次目录同步。
    """
    path = _path()
    payload = {"version": SCHEMA_VERSION, **values}
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=f".{path.name}.", suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, ensure_ascii=False, indent=2)
                handle.flush()
                os.fsync(handle.fileno())
            os.chmod(tmp, 0o600)
            os.replace(tmp, path)
        except BaseException:
            with contextlib.suppress(OSError):
                os.unlink(tmp)
            raise
    except OSError as exc:
        return False, f"{type(exc).__name__}: {exc}"
    return True, ""
