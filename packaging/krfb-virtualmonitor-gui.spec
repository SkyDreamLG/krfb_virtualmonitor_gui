# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller 打包配置（onedir）。

构建：packaging/build.sh
产物：dist/krfb-virtualmonitor-gui/ —— 可执行文件 + _internal/

三个刻意的选择：

  * **datas 里没有资源文件**。图标全是内嵌的 SVG 字符串（krfb_gui/ui/icons.py），
    词条是普通的 Python 模块，都不读磁盘、不用 qrc —— 没有东西需要打包进去。
    （密码存储走 D-Bus 调 KDE 钱包，也不需要任何元数据。）

  * **excludes 只列 Python 层模块**。Qt 的 .so 依赖由 PyInstaller 单独做二进制
    分析收集，跟这里无关 —— 所以排除未用到的模块不会导致运行时缺库，只是不再
    把用不到的那几十 MB Qt 库拖进来。
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

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    # Linux 上 console 选项不生效（只有 Windows/macOS 会据此切换子系统），
    # 保留终端输出反而便于排查启动失败。
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon= 在 Linux 上同样不生效，桌面图标由 packaging/*.svg + .desktop 负责
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name=APP_NAME,
)
