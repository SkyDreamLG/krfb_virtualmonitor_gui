#!/usr/bin/env python3
"""Krfb 虚拟屏管理器 —— 入口。

用法：
    python main.py            正常启动
    python main.py --tray     启动后直接缩到托盘（开机自启用这个）
"""

from __future__ import annotations

import argparse
import signal
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from PySide6.QtCore import QLockFile, QTimer  # noqa: E402
from PySide6.QtNetwork import QLocalServer, QLocalSocket  # noqa: E402
from PySide6.QtWidgets import QApplication, QMessageBox, QSystemTrayIcon  # noqa: E402

from krfb_gui import constants as C  # noqa: E402
from krfb_gui.i18n import tr  # noqa: E402
from krfb_gui.manager import Manager  # noqa: E402
from krfb_gui.secrets import Secrets  # noqa: E402
from krfb_gui.store import Store  # noqa: E402
from krfb_gui.ui import icons  # noqa: E402
from krfb_gui.ui.main_window import MainWindow  # noqa: E402
from krfb_gui.ui.theme import detect_palette, qt_palette, stylesheet  # noqa: E402


def _notify_existing() -> bool:
    """已经有实例在跑时，通知它把窗口显示出来。"""
    socket = QLocalSocket()
    socket.connectToServer(C.APP_ID)
    if socket.waitForConnected(500):
        socket.write(b"show")
        socket.flush()
        socket.waitForBytesWritten(500)
        socket.disconnectFromServer()
        return True
    return False


def main() -> int:
    # 命令行帮助也跟随语言（tr 首次调用时才去读 settings.json，这里已经是运行时）
    parser = argparse.ArgumentParser(description=tr(C.APP_NAME))
    parser.add_argument("--tray", action="store_true",
                        help=tr("Start minimized to the tray (used by autostart)"))
    parser.add_argument("--version", action="version",
                        version=f"{tr(C.APP_NAME)} {C.APP_VERSION}")
    args = parser.parse_args()

    app = QApplication(sys.argv)
    app.setApplicationName(C.APP_ID)
    app.setApplicationDisplayName(tr(C.APP_NAME))
    app.setApplicationVersion(C.APP_VERSION)
    # 不设的话 KDE 任务栏里会显示成 "python3"
    app.setDesktopFileName(C.APP_ID)
    app.setWindowIcon(icons.app_icon())
    # 关掉最后一个窗口不等于退出 —— 托盘还要继续活着，虚拟屏也要继续跑
    app.setQuitOnLastWindowClosed(False)

    # --- 单实例 ---
    C.RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    lock = QLockFile(str(C.LOCK_FILE))
    # 绝对不要设 setStaleLockTime(0) —— 那等于"永远不认为锁是陈旧的"。
    # 实测：程序被 SIGTERM 掉时锁文件不会被清理，于是后续每一次启动都被永久挡住。
    # 用默认 30 秒的判定，并在加锁失败时主动清一次陈旧锁再试。
    lock.setStaleLockTime(30_000)
    if not lock.tryLock(200) and not (lock.removeStaleLockFile() and lock.tryLock(200)):
        _notify_existing()
        return 0

    # 优雅处理 SIGTERM/SIGINT，让锁文件在退出时被正常释放
    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, lambda *_: app.quit())

    server = QLocalServer()
    QLocalServer.removeServer(C.APP_ID)
    server.listen(C.APP_ID)

    # --- 主题 ---
    # 先铺 QPalette 再上 QSS：只靠 QSS 的话窗口底色不会跟着主题走，
    # 会出现"暗色文字 + 亮色背景"的对比度灾难。
    palette = detect_palette(app)
    app.setPalette(qt_palette(palette))
    app.setStyleSheet(stylesheet(palette))

    # --- 组装 ---
    store = Store()
    store.load()
    store.prune_runtimes()
    secrets = Secrets()
    manager = Manager(store, secrets)

    window = MainWindow(palette, store, secrets, manager, start_in_tray=args.tray)

    def on_new_connection() -> None:
        socket = server.nextPendingConnection()
        if socket is not None:
            socket.readyRead.connect(lambda: _raise_window(window))
            socket.disconnected.connect(socket.deleteLater)

    def _raise_window(win: MainWindow) -> None:
        win.show()
        win.raise_()
        win.activateWindow()

    server.newConnection.connect(on_new_connection)

    if not args.tray:
        window.show()
    elif not QSystemTrayIcon.isSystemTrayAvailable():
        # 想缩到托盘但系统没有托盘 —— 那就正常显示，总比让用户找不到窗口好
        window.show()

    if store.load_error:
        QTimer.singleShot(300, lambda: QMessageBox.warning(
            window, tr("Config warning"), store.load_error
        ))

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
