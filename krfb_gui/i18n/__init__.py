"""界面文案国际化：英文原文即键，译文按语言分文件存放。

刻意只用标准库，且**不 import PySide6、不 import krfb_gui.store**：

  * `models` / `secrets` / `store` / `manager` 都是刻意保持 Qt-free、可单独
    跑测试的模块，而它们都要用 `tr()` 翻译错误文案；
  * `store` 需要 i18n 翻译它的 load_error，反向 import 会成环。偏好因此走
    `krfb_gui.prefs`（同样只用标准库），而不是 store。

两条铁律：

  * **绝不在 import 期调用 `tr()`** —— 界面语言随时可切，import 期冻结的
    文案再也跟不上；
  * **绝不把 `tr()` 结果存进会被比较、匹配或再次格式化的字段** ——
    只在渲染处翻译。运行态里的 `last_error` / `notes` 是事件记录，
    写入时是什么语言就是什么语言（见 `manager.py` 的说明）。

`tr()` 在 `paintEvent` 里也会被调用，所以首次惰性读盘之后只查内存。
"""

from __future__ import annotations

import os
from typing import Iterable

from .. import prefs
from .de import CATALOG as _DE
from .es import CATALOG as _ES
from .fr import CATALOG as _FR
from .it import CATALOG as _IT
from .ja import CATALOG as _JA
from .ko import CATALOG as _KO
from .pt_br import CATALOG as _PT_BR
from .ru import CATALOG as _RU
from .zh_cn import CATALOG as _ZH_CN
from .zh_tw import CATALOG as _ZH_TW

# 支持的语言。英文是原文（没有词条文件），其余各有一个词条模块。
LANGUAGES: tuple[str, ...] = (
    "zh_CN", "zh_TW", "ja", "ko", "de", "fr", "es", "it", "pt_BR", "ru", "en",
)

# 下拉框里的语言名永远用**母语**书写 —— 看不懂当前界面的用户也能找到自己那行。
_NATIVE_NAMES: dict[str, str] = {
    "zh_CN": "简体中文",
    "zh_TW": "繁體中文",
    "ja": "日本語",
    "ko": "한국어",
    "de": "Deutsch",
    "fr": "Français",
    "es": "Español",
    "it": "Italiano",
    "pt_BR": "Português (Brasil)",
    "ru": "Русский",
    "en": "English",
}

# 偏好值之一：跟随系统语言
SYSTEM = "system"

# 各语言的词条表（en 是原文，没有表）。测试与工具用得上，所以是公开的。
CATALOGS: dict[str, dict[str, str]] = {
    "zh_CN": _ZH_CN,
    "zh_TW": _ZH_TW,
    "ja": _JA,
    "ko": _KO,
    "de": _DE,
    "fr": _FR,
    "es": _ES,
    "it": _IT,
    "pt_BR": _PT_BR,
    "ru": _RU,
}

# 系统语言探测顺序。**空字符串一律当"未设置"跳过** —— `LC_ALL=` 很常见
# （本机就是），不跳过它会让中文环境莫名其妙地显示成英文。
_SYSTEM_ENV_ORDER = ("LC_ALL", "LC_MESSAGES", "LANGUAGE", "LANG")

_loaded = False
_preference = SYSTEM
_language = "en"


# --- 查询 --------------------------------------------------------------------
def tr(text: str) -> str:
    """把英文原文翻成当前语言。查不到就原样返回 —— 缺条目只能退化成英文，
    绝不能让界面出现空字符串。"""
    _ensure_loaded()
    return CATALOGS.get(_language, {}).get(text, text)


def trf(text: str, /, **params) -> str:
    """带占位符的 `tr()`：**先翻译、后替换**，顺序不可反 ——
    否则词条里的值会被当成格式串再解释一遍。"""
    return tr(text).format(**params)


def join_list(items: Iterable[str]) -> str:
    """按当前语言的顿号/逗号连接列表（中文目录里 ", " → "、"）。"""
    return tr(", ").join(items)


def for_lang(lang: str, text: str) -> str:
    """取指定语言的译文，不看当前偏好 —— 写 .desktop 的 Name[xx]= 用。"""
    return CATALOGS.get(lang, {}).get(text, text)


def language_name(pref: str) -> str:
    """下拉框里的显示名。"跟随系统"跟随当前界面语言，语言名永远是母语名。"""
    if pref == SYSTEM:
        return tr("Follow system")
    return _NATIVE_NAMES.get(pref, pref)


def current_language() -> str:
    """实际生效的语言（已解析过"跟随系统"）。"""
    _ensure_loaded()
    return _language


def preference() -> str:
    """用户选择：`system` 或某个受支持的语言代码。"""
    _ensure_loaded()
    return _preference


def available_preferences() -> tuple[str, ...]:
    return (SYSTEM, *LANGUAGES)


def match_locale(code: str) -> str | None:
    """把 `zh_TW` / `pt_BR` / `ja_JP` / `de` 这样的区域代码映射到受支持的语言。

    认不出这门语言时返回 None（调用方决定回退）。
    """
    parts = code.replace("-", "_").split("_")
    lang = parts[0].lower()
    rest = [part.upper() for part in parts[1:]]

    if lang == "zh":
        # 繁体区域（TW/HK/MO，或显式 Hant）→ 繁體，其余中文一律简体
        if any(part in ("TW", "HK", "MO", "HANT") for part in rest):
            return "zh_TW"
        return "zh_CN"
    if lang == "pt":
        # 目前只有巴西葡语词条，欧洲葡语也先用它
        return "pt_BR"
    return lang if lang in LANGUAGES else None


def detect_system_language(env: "dict[str, str] | None" = None) -> str:
    """从环境变量判断系统语言。纯函数，可单测。

    按 `LC_ALL → LC_MESSAGES → LANGUAGE → LANG` 取第一个非空变量，剥掉
    `.UTF-8` / `@latin` 后缀；`LANGUAGE` 是冒号分隔的候选列表，取第一个
    能认出来的。`C`/`POSIX` 表示"不要本地化"，直接英文。
    """
    env = os.environ if env is None else env
    for var in _SYSTEM_ENV_ORDER:
        value = (env.get(var) or "").strip()
        if not value:
            continue
        for entry in value.split(":"):
            code = entry.split(".", 1)[0].split("@", 1)[0]
            if not code:
                continue
            if code.upper() in ("C", "POSIX"):
                return "en"
            matched = match_locale(code)
            if matched:
                return matched
        # 这个变量里没有能认出来的语言 → 继续看下一个变量
    return "en"


def resolve(pref: "str | None", env: "dict[str, str] | None" = None) -> str:
    """偏好值 → 实际语言。未知值（含 None、空串、历史遗留）一律当跟随系统。"""
    if pref in LANGUAGES:
        return pref
    return detect_system_language(env)


# --- 变更 --------------------------------------------------------------------
def set_preference(pref: str) -> tuple[bool, str]:
    """切换语言并写盘，返回 (是否写盘成功, 错误信息)。

    写盘失败也照常切换（本次会话内有效）—— 与 `secrets` / 配置读取的
    降级哲学一致：绝不因为存不下偏好就拒绝用户的选择。
    """
    global _loaded, _preference, _language
    if pref not in available_preferences():
        pref = SYSTEM
    _loaded = True
    _preference = pref
    _language = resolve(pref)
    return prefs.set_value("language", pref)


def reload() -> None:
    """丢掉缓存、重读 settings.json（测试与将来的"重新载入"用）。"""
    global _loaded
    prefs.reload()
    _loaded = False
    _ensure_loaded()


# --- 内部 --------------------------------------------------------------------
def _ensure_loaded() -> None:
    """首次调用才读盘；之后只查内存。读盘永不可失败、永不建目录。"""
    global _loaded, _preference, _language
    if _loaded:
        return
    _loaded = True
    _preference = _read_preference()
    _language = resolve(_preference)


def _read_preference() -> str:
    pref = prefs.get("language", SYSTEM)
    # 文件里是垃圾值（或旧版本写下的）时按"跟随系统"处理
    return pref if pref in available_preferences() else SYSTEM
