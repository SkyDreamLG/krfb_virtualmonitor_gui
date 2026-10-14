# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller 打包配置（**单文件** onefile）。

构建：packaging/build-singlefile.sh
产物：dist/krfb-virtualmonitor-gui（一个可执行文件，约 170MB）

与 onedir 版的差别只有最后一段：把 binaries/datas 塞进 EXE 而不是 COLLECT。
代价是**每次启动都要把这 170MB 解压到 $TMPDIR**（本机 /tmp 是 tmpfs，等于写进内存），
而这是个常驻托盘、还要开机自启的程序 —— 启动慢一点、内存里多一份。
所以 onedir 仍然是默认构建（packaging/build.sh），单文件版是给"就想拷一个文件走"
的场景用的。两个 spec 的分析部分必须保持一致，改一个记得改另一个。
"""

from pathlib import Path

ROOT = Path(SPECPATH).parent  # packaging/ 的上一级，即仓库根
APP_NAME = "krfb-virtualmonitor-gui"

datas = []

# 程序实际只用到 QtCore / QtGui / QtWidgets / QtNetwork / QtSvg
# （QtNetwork 用于 QLocalServer 单实例，QtSvg 用于渲染内嵌图标）。
# 下面是 PySide6-Essentials 装进来、但本程序一次都没 import 的模块。
_QT_UNUSED = [
    "PySide6.QtConcurrent",
    "PySide6.QtDBus",
    "PySide6.QtDesigner",
    "PySide6.QtHelp",
    "PySide6.QtLabsStyleKit",
    "PySide6.QtOpenGL",
    "PySide6.QtOpenGLWidgets",
    "PySide6.QtPrintSupport",
    "PySide6.QtQml",
    "PySide6.QtQmlFeatures",
    "PySide6.QtQuick",
    "PySide6.QtQuickControls2",
    "PySide6.QtQuickTest",
    "PySide6.QtQuickWidgets",
    "PySide6.QtSql",
    "PySide6.QtSvgWidgets",
    "PySide6.QtTest",
    "PySide6.QtUiTools",
    "PySide6.QtXml",
]

a = Analysis(
    [str(ROOT / "main.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=datas,
    # 这几个 import 都在函数体内（各后端的 _connect / _decrypt 等），静态分析
    # 能找到，显式列出只是保险，防止将来被挪进 try/except 里而漏掉：
    #   * secretstorage / jeepney → 系统 Secret Service 后端、KDE 钱包后端的 D-Bus
    #   * cryptography            → 内置加密库的 Fernet
    #   * krfb_gui.secrets.*      → 三个后端模块（都是静态 import，写上无妨）
    hiddenimports=[
        "secretstorage",
        "jeepney",
        "cryptography",
        "krfb_gui.secrets.kwallet",
        "krfb_gui.secrets.secret_service",
        "krfb_gui.secrets.builtin",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[*_QT_UNUSED, "tkinter"],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

# 单文件：binaries/datas 直接进 EXE，没有 COLLECT
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,          # 上 upx 会被杀软误报，而且解压更慢
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # 解压位置：默认 $TMPDIR。本机它是 tmpfs，写进去等于占内存但读得飞快；
    # 换成磁盘目录（比如 /var/tmp）会把"启动慢"变成"启动更慢但省内存"，
    # 这里按默认来，别自作主张改用户的临时目录策略。
    runtime_tmpdir=None,
)
