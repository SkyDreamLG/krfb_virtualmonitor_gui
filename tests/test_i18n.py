"""国际化自检：词条完整性、系统语言探测、偏好落盘。

静态部分是核心：用 AST 扫描源码里所有 `tr()` / `trf()` 调用，保证
**每一条英文原文都有中文词条**、**词条里没有已废弃的孤儿**、
**源码里没有漏接 tr() 的中文字面量**。这三条覆盖了漏译的全部常见形态。

配置与状态写到临时目录（`/tmp/krfb-virtualmonitor-gui-i18n-test`，可用
KRBFTEST_DIR 改），不碰用户的真实配置 —— 见 isolate_config()。

    .venv/bin/python tests/test_i18n.py
"""

from __future__ import annotations

import ast
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# tr()/trf() 的调用名。`i18n.tr(...)` 这种带前缀的写法也要认。
_TR_FUNCS = {"tr", "trf"}

# 动态站点（参数不是字面量）必须在行尾标上这个注释，说明"这些 key 在别处生成"
_DYNAMIC_MARKER = "# i18n:dynamic"

# 动态站点消费的词条（值必须与代码里的取值集合保持一致）
_DYNAMIC_KEYS = {
    "not installed",   # main_window._krfb_version_source()
    "unknown",         # 同上
    "3:2 Tablet",      # constants.RESOLUTION_PRESETS 的 note 列（screen_dialog 遍历翻译）
    # autostart 写 .desktop 时用 for_lang() 取各语言的 Name/Comment，
    # 键来自模块常量，不走 tr()
    'Restore virtual screens marked as "desired running" at login',
    # packaging/install-desktop.sh 写应用菜单项时用的描述（shell 脚本，扫不到）
    "Manage krfb-virtualmonitor virtual screens",
}

# 扫描时豁免的文件：
#   * i18n/        —— 词条表本体，"中文就是数据"；
#   * ui/theme.py  —— 中文只出现在 QSS 内嵌注释里，不会渲染成文字。
_CJK_EXEMPT = {"krfb_gui/ui/theme.py"}
_CJK_EXEMPT_PREFIXES = ("krfb_gui/i18n/",)

_CJK_RE = re.compile(r"[㐀-鿿　-〿＀-￯]")


def isolate_config(base_dir: str | None = None) -> Path:
    """把配置指到临时目录 —— 绝不能写进用户的真实配置。

    必须在 import krfb_gui **之前**调用：`constants.py` 在导入时就把 CONFIG_DIR
    算好了（详见 tests/test_persistence.py 的同名函数）。
    """
    base = Path(base_dir or os.environ.get("KRBFTEST_DIR")
                or Path(tempfile.gettempdir()) / "krfb-virtualmonitor-gui-i18n-test")
    os.environ["XDG_CONFIG_HOME"] = str(base / "config")
    os.environ["XDG_STATE_HOME"] = str(base / "state")
    return base


# --- 静态扫描 ---------------------------------------------------------------
def _iter_sources():
    yield ROOT / "main.py"
    yield from sorted((ROOT / "krfb_gui").rglob("*.py"))


def _call_name(func: ast.expr) -> str | None:
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def _is_exempt(rel: str) -> bool:
    return rel in _CJK_EXEMPT or rel.startswith(_CJK_EXEMPT_PREFIXES)


def _docstring_ids(tree: ast.AST) -> set[int]:
    ids = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                             ast.AsyncFunctionDef)):
            if (node.body and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, ast.Constant)
                    and isinstance(node.body[0].value.value, str)):
                ids.add(id(node.body[0].value))
    return ids


def _is_app_name_arg(arg: ast.expr) -> bool:
    """识别 `tr(C.APP_NAME)`：参数是常量表里的应用名，本身就是一条词条。

    应用名在 13 处被引用，逐行标 # i18n:dynamic 只会变成噪声。
    """
    return isinstance(arg, ast.Attribute) and arg.attr == "APP_NAME"


def _app_name_key() -> str:
    from krfb_gui import constants as C
    return C.APP_NAME


def scan_sources() -> dict:
    """扫一遍全部源码，返回各类发现。

    tr() 参数**子树里的每个字符串常量**都算一个 key —— 这样
    `tr({状态: "Running", ...}[self])` 这种写法里的 6 个 key 也能被找到。
    子树里一个字符串常量都没有 = 动态站点，必须带 # i18n:dynamic。
    """
    literal_keys: dict[str, str] = {}     # key -> "path:line"
    dynamic_sites: list[tuple[str, int, bool]] = []   # (rel, line, marked)
    cjk_offenders: list[tuple[str, int, str]] = []

    for path in _iter_sources():
        rel = path.relative_to(ROOT).as_posix()
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        docstrings = _docstring_ids(tree)

        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or _call_name(node.func) not in _TR_FUNCS:
                continue
            if not node.args:
                continue
            arg = node.args[0]
            strings = [n for n in ast.walk(arg)
                       if isinstance(n, ast.Constant) and isinstance(n.value, str)
                       # 空串不是词条（比如 SecretsStatus.OK 的 detail 就是空串）
                       and n.value.strip()]
            if strings:
                for found in strings:
                    literal_keys.setdefault(found.value, f"{rel}:{found.lineno}")
            elif _is_app_name_arg(arg):
                literal_keys.setdefault(_app_name_key(), f"{rel}:{node.lineno}")
            elif not rel.startswith(_CJK_EXEMPT_PREFIXES):
                # i18n 引擎内部的 tr(text)（trf 的函数体）不算动态站点；
                # 其余动态站点必须带标记
                line = source.splitlines()[node.lineno - 1]
                dynamic_sites.append((rel, node.lineno, _DYNAMIC_MARKER in line))

        if _is_exempt(rel):
            continue
        for node in ast.walk(tree):
            if (isinstance(node, ast.Constant) and isinstance(node.value, str)
                    and id(node) not in docstrings and _CJK_RE.search(node.value)):
                cjk_offenders.append((rel, node.lineno, node.value[:50]))

    return {"keys": literal_keys, "dynamic": dynamic_sites, "cjk": cjk_offenders}


# --- 检查项 -----------------------------------------------------------------
def check_catalog_covers_literals() -> bool:
    """每条字面量 tr() 都要有词条 —— 漏译的主要防线（以简体表为准）。"""
    from krfb_gui.i18n import CATALOGS

    catalog = CATALOGS["zh_CN"]
    scan = scan_sources()
    missing = [f"{where}  {key!r}"
               for key, where in sorted(scan["keys"].items(), key=lambda kv: kv[1])
               if key not in catalog]
    if missing:
        print(f"  ✗ 以下 {len(missing)} 条原文没有词条：")
        for item in missing:
            print(f"      {item}")
        return False
    print(f"  ✓ {len(scan['keys'])} 条字面量原文都有词条")
    return True


def check_no_orphan_keys() -> bool:
    """词条表里没有源码已经不再使用的 key —— 防止改文案后留下死条目。"""
    from krfb_gui.i18n import CATALOGS

    catalog = CATALOGS["zh_CN"]
    scan = scan_sources()
    used = set(scan["keys"]) | _DYNAMIC_KEYS
    orphans = sorted(set(catalog) - used)
    if orphans:
        print(f"  ✗ {len(orphans)} 条词条已无源码使用：")
        for key in orphans:
            print(f"      {key!r}")
        return False
    stale_dynamic = sorted(_DYNAMIC_KEYS - set(catalog))
    if stale_dynamic:
        print(f"  ✗ 动态白名单里的 key 不在词条表中：{stale_dynamic}")
        return False
    print(f"  ✓ 词条表 {len(catalog)} 条，无孤儿")
    return True


def check_catalogs_complete() -> bool:
    """每种语言的词条表都必须是完整的 —— 缺条目会悄悄退回英文，
    在界面上表现为"夹生"的混语言，所以直接禁止。"""
    from krfb_gui.i18n import CATALOGS, LANGUAGES

    base = set(CATALOGS["zh_CN"])
    missing_langs = [lang for lang in LANGUAGES
                     if lang != "en" and lang not in CATALOGS]
    if missing_langs:
        print(f"  ✗ 这些语言没有词条表：{missing_langs}")
        return False

    ok = True
    for lang, catalog in sorted(CATALOGS.items()):
        missing = sorted(base - set(catalog))
        extra = sorted(set(catalog) - base)
        if missing or extra:
            ok = False
            print(f"  ✗ {lang}: 缺 {len(missing)} 条、多 {len(extra)} 条")
            for key in (missing + extra)[:6]:
                print(f"      {key!r}")
    if ok:
        print(f"  ✓ {len(CATALOGS)} 种语言 × {len(base)} 条词条，全部完整")
    return ok


def check_dynamic_sites_are_marked() -> bool:
    """参数不是字面量的 tr() 必须自带 # i18n:dynamic 标记。"""
    scan = scan_sources()
    unmarked = [f"{rel}:{line}" for rel, line, marked in scan["dynamic"] if not marked]
    if unmarked:
        print(f"  ✗ {len(unmarked)} 处动态 tr() 没有 {_DYNAMIC_MARKER} 标记：")
        for where in unmarked:
            print(f"      {where}")
        return False
    print(f"  ✓ {len(scan['dynamic'])} 处动态 tr() 都已标记")
    return True


def check_placeholder_parity() -> bool:
    """词条与原文的 {占位符} 集合必须一致 —— 抓 {nmae} 这类拼写错误。"""
    from string import Formatter

    from krfb_gui.i18n import CATALOGS

    formatter = Formatter()
    bad = []
    for lang, catalog in sorted(CATALOGS.items()):
        for key, value in catalog.items():
            try:
                key_fields = {name for _, name, _, _ in formatter.parse(key) if name}
                value_fields = {name for _, name, _, _ in formatter.parse(value) if name}
            except ValueError as exc:  # 词条里的花括号本身写坏了
                bad.append(f"{lang} {key!r}: 格式串无法解析（{exc}）")
                continue
            if key_fields != value_fields:
                bad.append(f"{lang} {key!r} → {value!r}\n"
                           f"        原文占位符 {sorted(key_fields)} "
                           f"≠ 词条 {sorted(value_fields)}")
    if bad:
        print(f"  ✗ {len(bad)} 条词条占位符不一致：")
        for item in bad:
            print(f"      {item}")
        return False
    print("  ✓ 各语言词条的占位符与原文完全一致")
    return True


def check_source_has_no_stray_cjk() -> bool:
    """非豁免文件里不应再有中文字面量 —— 漏接 tr() 的总兜底。

    豁免：词条表本体（i18n/）与 theme.py 的 QSS 内嵌注释。
    """
    scan = scan_sources()
    if scan["cjk"]:
        print(f"  ✗ {len(scan['cjk'])} 处中文字面量没有走 tr()：")
        for rel, line, text in scan["cjk"]:
            print(f"      {rel}:{line}  {text!r}")
        return False
    print("  ✓ 源码里没有漏接 tr() 的中文字面量")
    return True


def check_system_detection() -> bool:
    """系统语言探测：环境变量优先级与空值处理。"""
    from krfb_gui import i18n

    cases = [
        ({"LANG": "zh_CN.UTF-8"}, "zh_CN"),
        # LC_ALL="" 在本机很常见，必须当"未设置"跳过 —— 否则中文环境显示英文
        ({"LC_ALL": "", "LANG": "zh_CN.UTF-8"}, "zh_CN"),
        ({"LC_ALL": "  ", "LANG": "zh_CN.UTF-8"}, "zh_CN"),
        # LC_ALL 优先级更高
        ({"LC_ALL": "en_US.UTF-8", "LANG": "zh_CN.UTF-8"}, "en"),
        # C/POSIX = "不要本地化"，直接英文，且不再往下看
        ({"LC_ALL": "C", "LANG": "zh_CN.UTF-8"}, "en"),
        ({"LC_ALL": "POSIX"}, "en"),
        # LANGUAGE 是冒号分隔的候选列表，取第一个认识的
        ({"LANGUAGE": "zh_CN:en", "LANG": "en_US.UTF-8"}, "zh_CN"),
        ({"LANGUAGE": "en:zh_CN", "LANG": "zh_CN.UTF-8"}, "en"),
        ({"LANGUAGE": "sv_SE:de_DE", "LANG": "en_US.UTF-8"}, "de"),
        # 中文：繁体区域用繁体词条，其余一律简体
        ({"LANG": "zh_TW.UTF-8"}, "zh_TW"),
        ({"LANG": "zh_HK.UTF-8"}, "zh_TW"),
        ({"LANG": "zh_Hant_TW.UTF-8"}, "zh_TW"),
        ({"LANG": "zh_Hans_CN.UTF-8"}, "zh_CN"),
        ({"LANG": "zh_SG.UTF-8"}, "zh_CN"),
        # 各国语言
        ({"LANG": "ja_JP.UTF-8"}, "ja"),
        ({"LANG": "ko_KR.UTF-8"}, "ko"),
        ({"LANG": "de_DE@euro"}, "de"),
        ({"LANG": "fr_FR.UTF-8"}, "fr"),
        ({"LANG": "es_ES.UTF-8"}, "es"),
        ({"LANG": "it_IT.UTF-8"}, "it"),
        ({"LANG": "ru_RU.UTF-8"}, "ru"),
        # 葡语目前只有巴西词条，欧洲葡语也用它
        ({"LANG": "pt_BR.UTF-8"}, "pt_BR"),
        ({"LANG": "pt_PT.UTF-8"}, "pt_BR"),
        # 带连字符的写法（BCP 47）也认
        ({"LANG": "zh-TW"}, "zh_TW"),
        # 未支持的语言一律回退英文
        ({"LANG": "sv_SE.UTF-8"}, "en"),
        ({}, "en"),
    ]
    bad = [f"{env} → {got}（期望 {want}）"
           for env, want in cases
           if (got := i18n.detect_system_language(env)) != want]
    if bad:
        print(f"  ✗ {len(bad)} 条探测用例不通过：")
        for item in bad:
            print(f"      {item}")
        return False
    print(f"  ✓ 系统语言探测 {len(cases)} 条用例全部通过")
    return True


def check_preference_resolution() -> bool:
    """偏好值解析：显式值原样，其余（含垃圾值）都当跟随系统。"""
    from krfb_gui import i18n

    env = {"LANG": "zh_CN.UTF-8"}
    cases = [
        ("zh_CN", "zh_CN"), ("en", "en"), ("de", "de"), ("pt_BR", "pt_BR"),
        ("system", "zh_CN"), (None, "zh_CN"), ("", "zh_CN"),
        ("klingon", "zh_CN"),
    ]
    bad = [f"{pref!r} → {i18n.resolve(pref, env)}（期望 {want}）"
           for pref, want in cases
           if i18n.resolve(pref, env) != want]
    if bad:
        print(f"  ✗ {len(bad)} 条解析用例不通过：")
        for item in bad:
            print(f"      {item}")
        return False
    print(f"  ✓ 偏好解析 {len(cases)} 条用例全部通过")
    return True


def check_language_names() -> bool:
    """每种语言都要有唯一的显示名 —— 否则下拉框里会出现空行或两行一样。"""
    from krfb_gui import i18n

    prefs = i18n.available_preferences()
    names = [(pref, i18n.language_name(pref)) for pref in prefs]
    blank = [pref for pref, name in names if not name.strip()]
    if blank:
        print(f"  ✗ 这些语言没有显示名：{blank}")
        return False
    if len({name for _, name in names}) != len(names):
        print(f"  ✗ 显示名有重复：{names}")
        return False
    print(f"  ✓ {len(names)} 个语言项都有唯一的显示名")
    return True


def check_close_action_pref() -> bool:
    """关闭窗口的行为偏好：默认值、归一化、落盘、拒绝未知键。"""
    from krfb_gui import prefs

    prefs.reload()
    if prefs.close_action() != prefs.CLOSE_ASK:
        print(f"  ✗ 默认值应为 {prefs.CLOSE_ASK!r}，实际 {prefs.close_action()!r}")
        return False

    for value, expected in (("tray", "tray"), ("quit", "quit"), ("ask", "ask"),
                            ("garbage", "ask"), ("", "ask"), ("TRAY", "ask")):
        ok, error = prefs.set_close_action(value)
        if not ok:
            print(f"  ✗ 写入 {value!r} 失败：{error}")
            return False
        prefs.reload()
        if prefs.close_action() != expected:
            print(f"  ✗ 写入 {value!r} 后读回 {prefs.close_action()!r}"
                  f"（期望 {expected!r}）")
            return False

    ok, _ = prefs.set_value("nonsense", "x")
    if ok:
        print("  ✗ 未知偏好键竟然写成功了")
        return False
    print("  ✓ 关闭行为偏好：默认值/归一化/落盘/拒绝未知键均正常")
    return True


def check_tr_fallback() -> bool:
    """未命中的 key 原样返回；英文（原文）不需要词条；trf 正常替换。"""
    from krfb_gui import i18n

    i18n.set_preference("en")
    ok = i18n.tr("Running") == "Running" and i18n.tr("no such key") == "no such key"
    i18n.set_preference("zh_CN")
    ok = ok and i18n.tr("Running") == "运行中"
    ok = ok and i18n.tr("完全没见过的串") == "完全没见过的串"
    ok = ok and i18n.trf("Port {port} is already in use", port=5901) == "端口 5901 已被占用"
    ok = ok and i18n.join_list(["a", "b"]) == "a、b"
    if not ok:
        print("  ✗ tr()/trf() 回退或替换行为不对")
        return False
    print("  ✓ 未命中回退、英文直通、trf 替换、join_list 均正常")
    return True


def check_preference_roundtrip() -> bool:
    """落盘往返：写盘 → 文件内容 → 新进程读到同样的语言。"""
    from krfb_gui import constants as C
    from krfb_gui import i18n

    if not str(C.SETTINGS_FILE).startswith(str(isolate_config())):
        print(f"  ✗ SETTINGS_FILE 不在临时目录里：{C.SETTINGS_FILE}")
        return False

    ok, error = i18n.set_preference("en")
    if not ok:
        print(f"  ✗ 写盘失败：{error}")
        return False
    payload = json.loads(C.SETTINGS_FILE.read_text(encoding="utf-8"))
    if payload.get("language") != "en":
        print(f"  ✗ settings.json 里的语言不对：{payload}")
        return False
    mode = C.SETTINGS_FILE.stat().st_mode & 0o777
    if mode != 0o600:
        print(f"  ✗ settings.json 权限是 {oct(mode)}，期望 0o600")
        return False

    # 换个进程读 —— 同一进程内的缓存证明不了"重启后仍然生效"
    probe = ("import sys; sys.path.insert(0, %r);"
             "from krfb_gui import i18n;"
             "print(i18n.preference(), i18n.current_language(), i18n.tr('Running'))"
             % str(ROOT))
    proc = subprocess.run([sys.executable, "-c", probe], capture_output=True,
                          text=True, timeout=30, env=dict(os.environ))
    expected = "en en Running"
    if proc.returncode != 0 or proc.stdout.strip() != expected:
        print(f"  ✗ 新进程读到的是 {proc.stdout.strip()!r}"
              f"（期望 {expected!r}），stderr={proc.stderr.strip()[:200]}")
        return False

    i18n.set_preference("zh_CN")
    if i18n.tr("Running") != "运行中":
        print("  ✗ 切回中文没有立即生效")
        return False
    print("  ✓ 落盘内容/权限正确，新进程能读到，切换立即生效")
    return True


def check_broken_settings() -> bool:
    """坏 settings.json 不许抛异常、不许建目录，一律退回"跟随系统"。"""
    from krfb_gui import constants as C
    from krfb_gui import i18n

    path = C.SETTINGS_FILE
    cases = {
        "文件缺失": None,
        "坏 JSON": "{ not json",
        "不是 dict": '["en"]',
        "语言值不认识": '{"version": 1, "language": "klingon"}',
        "版本无关但字段缺失": '{"version": 99}',
    }
    for title, content in cases.items():
        if content is None:
            path.unlink(missing_ok=True)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        try:
            i18n.reload()
        except Exception as exc:  # noqa: BLE001 - 就是要证明它不会抛
            print(f"  ✗ {title} 时 reload() 抛了 {type(exc).__name__}: {exc}")
            return False
        if i18n.preference() != "system":
            print(f"  ✗ {title} 时偏好是 {i18n.preference()!r}，期望 'system'")
            return False
    print(f"  ✓ {len(cases)} 种坏文件都静默回退到跟随系统")
    return True


def check_i18n_is_qt_free() -> bool:
    """i18n 必须保持 Qt-free：核心层（models/secrets/store/manager）全靠这一点
    才能脱离界面单独测试。"""
    probe = ("import sys; sys.path.insert(0, %r);"
             "import krfb_gui.i18n;"
             "print('PySide6' in sys.modules)" % str(ROOT))
    proc = subprocess.run([sys.executable, "-c", probe], capture_output=True,
                          text=True, timeout=30, env=dict(os.environ))
    if proc.returncode != 0:
        print(f"  ✗ 导入 krfb_gui.i18n 失败：{proc.stderr.strip()[:200]}")
        return False
    if proc.stdout.strip() != "False":
        print("  ✗ i18n 把 PySide6 也拖进来了")
        return False
    print("  ✓ i18n 只依赖标准库，没有引入 PySide6")
    return True


def main() -> int:
    isolate_config()
    # isolate 之后再 import krfb_gui —— 各个检查里都是惰性 import 的
    checks = (
        ("词条覆盖所有字面量 tr()", check_catalog_covers_literals),
        ("词条表没有孤儿", check_no_orphan_keys),
        ("各语言词条完整", check_catalogs_complete),
        ("动态 tr() 已标记", check_dynamic_sites_are_marked),
        ("占位符一一对应", check_placeholder_parity),
        ("源码无漏接的中文", check_source_has_no_stray_cjk),
        ("语言显示名", check_language_names),
        ("系统语言探测", check_system_detection),
        ("偏好解析与回退", check_preference_resolution),
        ("tr() 回退行为", check_tr_fallback),
        ("偏好落盘往返", check_preference_roundtrip),
        ("关闭行为偏好", check_close_action_pref),
        ("坏配置文件鲁棒性", check_broken_settings),
        ("i18n 保持 Qt-free", check_i18n_is_qt_free),
    )

    failed = 0
    for title, check in checks:
        print(f"{title}:")
        try:
            ok = check()
        except Exception as exc:  # 让一项失败不要吞掉其它项
            print(f"  ✗ 抛异常：{type(exc).__name__}: {exc}")
            ok = False
        failed += 0 if ok else 1

    print(f"\n失败 {failed} 项")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
