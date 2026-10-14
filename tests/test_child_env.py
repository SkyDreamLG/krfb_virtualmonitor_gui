"""打包版子进程环境回归测试：PyInstaller 注入的 LD_LIBRARY_PATH 不得外泄给外部命令。

背景（已在本机实测）：PyInstaller 的 Linux 启动器会往 GUI **自己**的环境里注入
`LD_LIBRARY_PATH=<包内 _internal>:<原值>`（原值另存为 `LD_LIBRARY_PATH_ORIG`）。
本程序要调用的系统助手程序也是 Qt 程序，继承过去就会绑到包内 libQt6 上：

    $ LD_LIBRARY_PATH=dist/krfb-virtualmonitor-gui/_internal kscreen-doctor -o
    qt.qpa.plugin: Could not find the Qt platform plugin "wayland" in ""
    → exit 134（SIGABRT），stdout 全空

后果不是"少个提示"：`kscreen.list_outputs()` 永远返回空 → 启动成功判定永久失败 →
8 秒后误报超时（还把运行记录抹掉，进程变成孤儿，用户必须先「扫描」才能重新纳管）。

    .venv/bin/python tests/test_child_env.py

修复前第 1/2/4 项必然失败，修复后应全绿。不碰真实配置、不需要打包产物、
不弹 GUI；缺 kscreen-doctor / krfb-virtualmonitor 时相应检查自动跳过。
"""

from __future__ import annotations

import ast
import contextlib
import os
import shutil
import socket
import subprocess
import sys
import tempfile
from collections.abc import Iterator
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# 替身 kscreen-doctor：只要继承了 LD_LIBRARY_PATH 就死 —— 真程序被污染时就是这样
# （加载不到平台插件 → abort、stdout 全空）。比真程序更严格，但这正是要守的规矩。
SHIM_POISONED_DIES = """#!/bin/sh
if [ -n "${LD_LIBRARY_PATH:-}" ]; then
    echo 'qt.qpa.plugin: Could not find the Qt platform plugin "wayland" in ""' >&2
    exit 134
fi
"""
SHIM_OUTPUT = """
echo "Output: 1 Virtual-Test 27e99bcc-7f5c-4b19-8a2e-000000000001"
echo "    enabled"
echo "    Modes: 38:2736x1824@60.00*!"
echo "    Geometry: 0,0 2736x1824"
echo "    Scale: 1.0"
"""


@contextlib.contextmanager
def _env(changes: dict[str, str | None]) -> Iterator[None]:
    """临时改写 os.environ（None = 删除），退出时原样还原。"""
    saved = {key: os.environ.get(key) for key in changes}
    for key, value in changes.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value
    try:
        yield
    finally:
        for key, value in saved.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def _poison_dirs() -> list[Path]:
    """能真正毒死系统 Qt 程序的目录，按"最忠实"排序。

    关键是要有一个**和系统不同版本**的 libQt6Core.so.6 排在搜索路径前面。
    真实打包目录最忠实；其次 .venv 里 PySide6 自带的 Qt（同一台机器上必然存在，
    所以本测试不需要先构建就能复现）。
    """
    candidates = [
        ROOT / "dist" / "krfb-virtualmonitor-gui" / "_internal",
        ROOT / ".venv" / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}"
        / "site-packages" / "PySide6" / "Qt" / "lib",
    ]
    return [path for path in candidates if (path / "libQt6Core.so.6").exists()]


@contextlib.contextmanager
def _packed_env(poison: Path | None) -> Iterator[None]:
    """模拟打包版进程的环境。"""
    value = str(poison) if poison is not None else "/nonexistent-krfb-test"
    with _env({"LD_LIBRARY_PATH": value, "LD_LIBRARY_PATH_ORIG": "/nonexistent-orig"}):
        yield


def _probe(argv: list[str]) -> str:
    """老写法：直接 subprocess，继承当前环境。用来量基线与自检污染是否有效。"""
    try:
        proc = subprocess.run(argv, capture_output=True, text=True, timeout=8, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return proc.stdout or ""


def _write_shim(directory: Path, body: str) -> None:
    """把 body 写成替身 kscreen-doctor（名字必须和 kscreen.KSCREEN_DOCTOR 一致）。"""
    from krfb_gui.kscreen import KSCREEN_DOCTOR

    shim = directory / KSCREEN_DOCTOR
    shim.write_text(body, encoding="utf-8")
    shim.chmod(0o755)


def check_whitelist() -> bool:
    """child_env() 只透传白名单：LD_*/QT_*/PYTHON* 全剥掉，桌面必需变量保留。"""
    from krfb_gui import envtools

    poison = _poison_dirs()[0] if _poison_dirs() else None
    with _packed_env(poison):
        os.environ["PYTHONPATH"] = "/opt/ros/lyrical/lib/python"
        os.environ["QT_QPA_PLATFORM"] = "offscreen"
        env = envtools.child_env()

    problems = [
        f"剥漏了 {key}"
        for key in ("LD_LIBRARY_PATH", "LD_LIBRARY_PATH_ORIG", "PYTHONPATH",
                    "QT_QPA_PLATFORM", "VIRTUAL_ENV")
        if key in env
    ]
    problems += [
        f"丢掉了必需的 {key}"
        for key in ("PATH", "HOME", "WAYLAND_DISPLAY", "XDG_RUNTIME_DIR",
                    "DBUS_SESSION_BUS_ADDRESS")
        if os.environ.get(key) and key not in env
    ]
    if problems:
        print("  ✗ " + "；".join(problems))
        return False
    print("  ✓ 白名单正确：LD_*/QT_*/PYTHON* 全剥掉，桌面必需变量保留")
    return True


def check_kscreen_uses_clean_env() -> bool:
    """被污染时 kscreen.list_outputs() 仍要能拿到输出 —— 本次 bug 的核心复现。

    用替身二进制，所以不依赖真的 kscreen-doctor、不依赖打包产物、不依赖显示环境；
    跑的是**生产代码路径**（kscreen._run → envtools.run_helper → subprocess）。
    """
    from krfb_gui import kscreen

    with tempfile.TemporaryDirectory(prefix="krfbtest-bin-") as tmp:
        _write_shim(Path(tmp), SHIM_POISONED_DIES + SHIM_OUTPUT)
        with _env({"PATH": f"{tmp}:{os.environ.get('PATH', '')}"}), _packed_env(None):
            outputs = kscreen.list_outputs()

    if not outputs:
        print("  ✗ 子进程继承了 LD_LIBRARY_PATH（替身 kscreen-doctor 被毒死，输出为空）")
        return False
    out = outputs[0]
    if (out.connector, out.width, out.height, out.scale) != ("Virtual-Test", 2736, 1824, 1.0):
        print(f"  ✗ 解析结果不对：{out!r}")
        return False
    print("  ✓ 被污染时 kscreen-doctor 仍被正常执行并解析")
    return True


def check_real_helpers() -> bool | None:
    """真的 kscreen-doctor / krfb-virtualmonitor，配上真的打包污染。

    先自检"这层污染确实能让老写法失败"，否则这次模拟是空转 —— 跳过，而不是假绿。
    """
    from krfb_gui import envtools, kscreen, proctools

    kscreen_bin = shutil.which(kscreen.KSCREEN_DOCTOR)
    krfb_bin = proctools.krfb_binary()
    if kscreen_bin is None and krfb_bin is None:
        print("  · 本机没有 kscreen-doctor / krfb-virtualmonitor，跳过")
        return None

    poison_dirs = _poison_dirs()
    if not poison_dirs:
        print("  · 找不到能和系统 Qt 冲突的 libQt6（dist/ 与 .venv 都没有），跳过")
        return None

    with _packed_env(poison_dirs[0]):
        # 自检：老写法（继承本进程环境）必须真的被毒死
        legacy_ok = False
        if kscreen_bin:
            legacy_ok = "Output:" in _probe([kscreen_bin, "-o"])
        if krfb_bin:
            legacy_ok = legacy_ok or "krfb-virtualmonitor" in _probe([krfb_bin, "--version"])
        if legacy_ok:
            print("  · 模拟污染在这台机器上无效（老写法照样跑通），跳过真实二进制比对")
            return None

        problems = []
        if kscreen_bin:
            outputs = kscreen.list_outputs()
            if not outputs:
                problems.append(f"污染后 kscreen-doctor 回读不到任何输出（{poison_dirs[0]}）")
        if krfb_bin:
            proc = envtools.run_helper([krfb_bin, "--version"], timeout=4)
            text = (proc.stdout or proc.stderr).strip() if proc else ""
            if not text.startswith("krfb-virtualmonitor"):
                problems.append(f"污染后 --version 探测不可信：{text!r}")

    if problems:
        for text in problems:
            print(f"  ✗ {text}")
        return False
    print(f"  ✓ 污染下真实助手仍可用（污染源 {poison_dirs[0].relative_to(ROOT)}）")
    return True


def check_kwin_fallback() -> bool:
    """问不到 KWin 时 output_ready() 退化为端口判据；问得到时必须保持严格。

    这条守的是"虚拟屏明明起来了却误报失败"那一类事故 —— 误报会抹掉运行记录，
    把进程变成孤儿（packaged build 的表象就是这么来的）。
    """
    from krfb_gui import kscreen
    from krfb_gui.manager import Manager
    from krfb_gui.models import Screen
    from krfb_gui.secrets import Secrets
    from krfb_gui.store import Store

    manager = Manager(Store(), Secrets())
    # 监听一个真实端口：proctools 是纯 /proc 读取，所以这里必须真监听
    server = socket.socket()
    server.bind(("127.0.0.1", 0))
    server.listen(1)
    port = server.getsockname()[1]

    try:
        # 屏幕名刻意不叫 Test，好让"好"替身里没有这个 connector
        screen = Screen(name="Strict", width=1920, height=1080, scale=1.0, port=port)

        with tempfile.TemporaryDirectory(prefix="krfbtest-silent-") as silent:
            # 能起来但什么都不输出 —— 等价于"问不到 KWin"
            _write_shim(Path(silent), "#!/bin/sh\nexit 0\n")
            with _env({"PATH": f"{silent}:{os.environ.get('PATH', '')}"}):
                if kscreen.usable():
                    print("  ✗ 替身没有任何输出，usable() 却报 True")
                    return False
                if not manager.output_ready(screen):
                    print("  ✗ 问不到 KWin 时没有退化为端口判据（虚拟屏会因此被误报失败）")
                    return False

        with tempfile.TemporaryDirectory(prefix="krfbtest-good-") as good:
            _write_shim(Path(good), "#!/bin/sh\n" + SHIM_OUTPUT)
            with _env({"PATH": f"{good}:{os.environ.get('PATH', '')}"}):
                if not kscreen.usable():
                    print("  ✗ 替身能正常输出，usable() 却报 False")
                    return False
                if manager.output_ready(screen):
                    print("  ✗ 问得到 KWin 时应该保持严格，却按端口放行了")
                    return False
    finally:
        server.close()

    print("  ✓ 问不到 KWin 时退化为端口判据；问得到时保持严格")
    return True


def check_no_bare_subprocess() -> bool:
    """krfb_gui 下每个 subprocess 调用都必须显式传 env=。

    这条规则就是本次 bug 的根因（默认继承 os.environ，打包版里带着 PyInstaller
    注入的 LD_LIBRARY_PATH）。统一走 envtools.run_helper() 就自然满足它，
    而且这条静态规则能让将来新增的调用点也躲不过。
    """
    offenders: list[str] = []
    for path in sorted((ROOT / "krfb_gui").rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if not (
                isinstance(func, ast.Attribute)
                and isinstance(func.value, ast.Name)
                and func.value.id == "subprocess"
            ):
                continue
            if not any(keyword.arg == "env" for keyword in node.keywords):
                offenders.append(
                    f"{path.relative_to(ROOT)}:{node.lineno} subprocess.{func.attr}() 没传 env="
                )

    if offenders:
        print("  ✗ 这些外部命令会继承本进程环境（打包版下带着包内 Qt6）：")
        for text in offenders:
            print(f"      {text}")
        return False
    print("  ✓ krfb_gui 下所有 subprocess 调用都指定了 env=")
    return True


def main() -> int:
    checks = (
        ("子进程环境白名单", check_whitelist),
        ("kscreen-doctor 调用（替身，必定执行）", check_kscreen_uses_clean_env),
        ("真实助手程序（污染确实有效才比对）", check_real_helpers),
        ("问不到 KWin 时的降级", check_kwin_fallback),
        ("没有裸的 subprocess 调用", check_no_bare_subprocess),
    )
    results = []
    for title, check in checks:
        print(f"{title}:")
        results.append(check())

    passed = sum(1 for r in results if r is True)
    skipped = sum(1 for r in results if r is None)
    failed = sum(1 for r in results if r is False)
    print(f"\n通过 {passed}，跳过 {skipped}，失败 {failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
