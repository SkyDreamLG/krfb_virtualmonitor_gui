"""主窗口：左列表 + 右详情，外加顶部通知条、工具栏、状态栏与系统托盘。"""

from __future__ import annotations

import threading
import time

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QAction, QPainter
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QSplitter,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)

from .. import constants as C
from .. import envtools, prefs, proctools
from ..i18n import join_list, tr, trf
from ..manager import Manager
from ..models import Runtime, Screen, ScreenState
from ..secrets import SecretTimeout, Secrets, SecretsStatus
from ..store import Store
from . import icons
from .detail_pane import DetailPane
from .dialogs import AdoptDialog, PasswordPrompt, SettingsDialog
from .log_viewer import LogViewer
from .screen_dialog import ScreenDialog
from .screen_list import ScreenList
from .theme import Palette, with_alpha
from .vector import Clock, LogoMark

# 启动后多久等不到 KWin 输出就判定失败。
# 秒数是数字，直接用它拼句子的**函数**在下面 —— 不能在这里预先拼成字符串：
# import 期冻结的文案跟不上语言切换（而且它还会被写进 runtime.json）。
VERIFY_TIMEOUT_S = C.SPAWN_VERIFY_TIMEOUT_MS / 1000


class NoticeBar(QWidget):
    """顶部通知条。淡入 + 高度展开，不用 QGraphicsOpacityEffect。"""

    action_clicked = Signal()
    closed = Signal()

    def __init__(self, palette: Palette, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._palette = palette
        self._tone = "warning"
        self._alpha = 1.0
        self.setFixedHeight(0)
        self.hide()

        self._icon = QLabel()
        self._icon.setFixedSize(18, 18)
        self._text = QLabel()
        self._text.setWordWrap(False)
        self._action = QPushButton(tr("Restart"))
        self._action.setProperty("accent", True)
        self._action.clicked.connect(self.action_clicked)
        self._close = QPushButton()
        self._close.setFlat(True)
        self._close.setFixedSize(24, 24)
        self._close.setIcon(icons.icon("close", palette.color("text_dim"), 13))
        icons.mark_icon_only(self._close)
        self._close.clicked.connect(self.closed)

        row = QHBoxLayout(self)
        row.setContentsMargins(16, 0, 10, 0)
        row.setSpacing(9)
        row.addWidget(self._icon)
        row.addWidget(self._text, 1)
        row.addWidget(self._action)
        row.addWidget(self._close)

        self._anim = QTimer(self)
        self._anim.setInterval(16)
        self._anim.timeout.connect(self._step)
        self._target = 0
        self._height = 0.0
        self._fade_target = 1.0
        self._starting = True
        self._hiding = False
        self._rebuild = None

    def show_message(self, text: str, action: str = "", tone: str = "warning",
                     *, rebuild=None) -> None:
        """`rebuild` 是零参回调，返回 (text, action)：横幅文案是 per-message 的，
        没有固定的 key 可以重新 tr()，语言切换后只能靠它按当前语言重算。"""
        self._rebuild = rebuild
        self._apply(text, action, tone)
        self.show()
        self._starting = True
        self._hiding = False
        self._alpha = 0.0
        self._height = 0.0
        self._target = 42
        self._fade_target = 1.0
        self._anim.start()

    def _apply(self, text: str, action: str, tone: str) -> None:
        self._tone = tone
        self._text.setText(text)
        icon_kind = "warning" if tone in ("warning", "danger") else "info"
        self._icon.setPixmap(icons.pixmap(icon_kind, self._palette.color(tone), 18))
        self._action.setVisible(bool(action))
        if action:
            self._action.setText(action)

    def retranslate(self) -> None:
        """语言切换后重放当前消息。已经收起或正在收起的不复活 —— 用户关掉了它。"""
        if self._rebuild is None or self._hiding or self._target == 0:
            return
        rebuilt = self._rebuild()
        if rebuilt and rebuilt[0]:
            self._apply(rebuilt[0], rebuilt[1], self._tone)

    def _step(self) -> None:
        speed = 0.22
        self._height += (self._target - self._height) * speed
        self._alpha += (self._fade_target - self._alpha) * speed
        if abs(self._height - self._target) < 0.6:
            self._height = float(self._target)
        if abs(self._alpha - self._fade_target) < 0.02:
            self._alpha = self._fade_target
        self.setFixedHeight(int(self._height))
        self.update()

        if self._hiding and self._alpha < 0.03 and self._height < 1:
            self._anim.stop()
            self.hide()
        elif not self._hiding and self._height == self._target and self._alpha == self._fade_target:
            self._anim.stop()

    def fade_out(self) -> None:
        self._hiding = True
        self._target = 0
        self._fade_target = 0.0
        self._anim.start()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setOpacity(self._alpha)

        rect = self.rect().adjusted(0, 2, 0, -2)
        color = self._palette.color(self._tone)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(with_alpha(color, 0.13))
        painter.drawRoundedRect(rect, 8, 8)
        painter.setBrush(color)
        painter.drawRoundedRect(rect.left() + 1, rect.top() + 6, 3, rect.height() - 12, 1.5, 1.5)


class MainWindow(QMainWindow):
    # 后台解锁结束 → 主线程收尾（跨线程 emit 会被 Qt 排队）
    unlock_finished = Signal(bool)

    def __init__(self, palette: Palette, store: Store, secrets: Secrets,
                 manager: Manager, start_in_tray: bool = False) -> None:
        super().__init__()
        self._palette = palette
        self._store = store
        self._secrets = secrets
        self._manager = manager

        self._clock = Clock()
        self._log_windows: dict[str, LogViewer] = {}
        self._pending: dict[str, float] = {}      # screen_id -> 验证截止时间
        self._notified_crash: set[str] = set()
        self._crashed_now: list[str] = []
        # 通知条只有一个操作按钮，用 mode 决定它做什么，避免反复 connect/disconnect
        self._notice_mode = "crash"
        self._really_quit = False
        self._tray_hint_shown = False
        # environment_warnings() 返回的是拼好的成品文案（语言相关），
        # 语言切换时要整份重算，见 _warnings()
        self._warnings_cache: list[str] | None = None

        self.setWindowTitle(tr(C.APP_NAME))
        self.setWindowIcon(icons.app_icon())
        self.setMinimumSize(*C.WINDOW_MIN_SIZE)
        self.resize(*C.WINDOW_DEFAULT_SIZE)

        # 后台申请解锁密钥环的相关状态
        self._unlock_running = False
        self._unlock_explicit = False   # 是用户点"解锁密钥环"发起的吗
        self._pending_start_all = False

        self._build_ui()
        self._build_tray()

        self._timer = QTimer(self)
        self._timer.setInterval(C.POLL_INTERVAL_MS)
        self._timer.timeout.connect(self._refresh)
        self._timer.start()

        self.unlock_finished.connect(self._on_unlock_finished)
        self._secrets.probe()
        self._refresh()
        self._startup_report(start_in_tray)

    # ---------------------------------------------------------------- 密钥环
    def _request_unlock(self, *, automatic: bool) -> None:
        """申请解锁密钥环 —— 锁着的话读不到已保存的密码。

        `unlock()` 会弹系统提示框（ksecretd / gnome-keyring）并可能等上几十秒，
        所以整个调用丢进后台线程，界面照常可用；超时仍在 `secrets` 那边兜底，
        最坏退化成"本次会话内存"。
        """
        if self._secrets.status is not SecretsStatus.LOCKED:
            return
        if self._unlock_running:
            # 已经有一次在等系统提示框了。用户此刻又点了一次按钮 → 升级成
            # "显式"，让结果弹框告诉他，而不是只飘一条通知。
            self._unlock_explicit = self._unlock_explicit or not automatic
            return
        if automatic and not self._store.screens:
            return  # 一个虚拟屏都没有，没必要为此弹钥匙串
        self._unlock_explicit = not automatic
        self._unlock_running = True
        threading.Thread(target=self._unlock_worker, daemon=True,
                         name="keyring-unlock").start()

    def _unlock_worker(self) -> None:
        unlocked = self._secrets.try_unlock()
        # 跨线程 emit：Qt 会把它排队到主线程，界面操作只在主线程做
        self.unlock_finished.emit(unlocked)

    def _on_unlock_finished(self, unlocked: bool) -> None:
        self._unlock_running = False
        explicit, self._unlock_explicit = self._unlock_explicit, False
        if self._pending_start_all:
            # 托盘自启时等解锁完再启动屏幕：锁着读不到密码，起了也白起
            self._pending_start_all = False
            self._on_start_all()
        self._refresh()

        if unlocked:
            if explicit:
                QMessageBox.information(
                    self, tr("Keyring"),
                    tr("Unlocked. Passwords will be saved to the keyring."),
                )
            return

        message = tr("Unlock failed or timed out. Passwords can still be used for "
                     "this session, but must be re-entered after quitting.")
        if explicit:
            QMessageBox.warning(self, tr("Keyring"), message)
        else:
            # 启动时自动尝试的那种：不弹框打断，飘一条通知就够
            self._notice_mode = "info"
            self._notice.show_message(message, "", "warning")
            QTimer.singleShot(6000, self._notice.fade_out)

    def _warnings(self, *, force: bool = False) -> list[str]:
        """环境检查结果。字符串由 manager 拼好（文案写死在代码里），所以语言
        切换后必须 force 重算 —— 缓存里是"当时语言"的成品。"""
        if self._warnings_cache is None or force:
            self._warnings_cache = self._manager.environment_warnings()
        return self._warnings_cache

    # ---------------------------------------------------------------- 界面
    def _build_ui(self) -> None:
        central = QWidget()
        central.setObjectName("central")
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(14, 12, 14, 8)
        root.setSpacing(9)

        # --- 标题栏 ---
        header = QHBoxLayout()
        header.setSpacing(11)

        logo = LogoMark(self._clock, self._palette, 30)
        header.addWidget(logo)

        titles = QVBoxLayout()
        titles.setSpacing(0)
        self._title = QLabel(tr(C.APP_NAME))
        self._title.setProperty("role", "title")
        self._subtitle = QLabel(tr("Graphical manager for krfb-virtualmonitor"))
        self._subtitle.setProperty("role", "faint")
        titles.addWidget(self._title)
        titles.addWidget(self._subtitle)
        header.addLayout(titles)
        header.addStretch(1)

        # 前导空格是给图标留的位，刻意留在 tr() 外面 —— 词条里不该有空白
        self._btn_new = QPushButton("  " + tr("New virtual screen"))
        self._btn_new.setProperty("accent", True)
        self._btn_new.setIcon(icons.icon("plus", "#ffffff", 15))
        self._btn_new.clicked.connect(self._on_new)

        self._btn_start_all = QPushButton(tr("Start all"))
        self._btn_start_all.setIcon(icons.icon("play", self._palette.color("text"), 13))
        self._btn_start_all.clicked.connect(self._on_start_all)

        self._btn_stop_all = QPushButton(tr("Stop all"))
        self._btn_stop_all.setIcon(icons.icon("stop", self._palette.color("text"), 13))
        self._btn_stop_all.clicked.connect(self._on_stop_all)

        self._btn_scan = QPushButton()
        self._btn_scan.setIcon(icons.icon("scan", self._palette.color("text"), 15))
        self._btn_scan.setToolTip(tr("Scan for and adopt krfb processes "
                                     "started outside this app"))
        icons.mark_icon_only(self._btn_scan)
        self._btn_scan.setFixedWidth(38)
        self._btn_scan.clicked.connect(self._on_scan)

        self._btn_refresh = QPushButton()
        self._btn_refresh.setIcon(icons.icon("refresh", self._palette.color("text"), 15))
        self._btn_refresh.setToolTip(tr("Refresh now"))
        icons.mark_icon_only(self._btn_refresh)
        self._btn_refresh.setFixedWidth(38)
        self._btn_refresh.clicked.connect(self._refresh)

        self._btn_settings = QPushButton()
        self._btn_settings.setIcon(icons.icon("tune", self._palette.color("text"), 15))
        self._btn_settings.setToolTip(tr("Settings"))
        icons.mark_icon_only(self._btn_settings)
        self._btn_settings.setFixedWidth(38)
        self._btn_settings.clicked.connect(self._on_settings)

        for button in (self._btn_new, self._btn_start_all, self._btn_stop_all,
                       self._btn_scan, self._btn_refresh, self._btn_settings):
            header.addWidget(button)
        root.addLayout(header)

        # --- 通知条 ---
        self._notice = NoticeBar(self._palette)
        self._notice.action_clicked.connect(self._on_notice_action)
        self._notice.closed.connect(self._on_notice_closed)
        root.addWidget(self._notice)

        # --- 主体：分割器 ---
        self._list = ScreenList(self._palette, self._clock)
        self._list.selection_changed.connect(self._on_selection)
        self._list.row_activated.connect(self._on_row_activated)

        self._detail = DetailPane(self._palette)
        self._detail.start_requested.connect(self._on_start)
        self._detail.stop_requested.connect(self._on_stop)
        self._detail.edit_requested.connect(self._on_edit)
        self._detail.log_requested.connect(self._on_log)
        self._detail.delete_requested.connect(self._on_delete)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self._list)
        splitter.addWidget(self._detail)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([C.SIDEBAR_WIDTH, 640])
        splitter.setChildrenCollapsible(False)
        root.addWidget(splitter, 1)

        # --- 状态栏 ---
        self._status_left = QLabel()
        self._status_left.setProperty("role", "faint")
        self._status_right = QLabel()
        self._status_right.setProperty("role", "faint")
        self.statusBar().addWidget(self._status_left, 1)
        self.statusBar().addPermanentWidget(self._status_right)

    def _build_tray(self) -> None:
        self._tray: QSystemTrayIcon | None = None
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return

        self._tray = QSystemTrayIcon(icons.app_icon(), self)
        self._tray.setToolTip(tr(C.APP_NAME))

        menu = self._tray_menu = QMenu()

        self._act_show = QAction(tr("Show main window"), self)
        self._act_show.triggered.connect(self._show_window)
        menu.addAction(self._act_show)
        menu.addSeparator()

        self._act_start_all = QAction(tr("Start all"), self)
        self._act_start_all.triggered.connect(self._on_start_all)
        menu.addAction(self._act_start_all)

        self._act_stop_all = QAction(tr("Stop all"), self)
        self._act_stop_all.triggered.connect(self._on_stop_all)
        menu.addAction(self._act_stop_all)
        menu.addSeparator()

        self._act_quit = QAction(tr("Quit"), self)
        self._act_quit.triggered.connect(self._quit)
        menu.addAction(self._act_quit)

        # Wayland 下从 activated 里 popup() 位置会被忽略，必须用 setContextMenu
        self._tray.setContextMenu(menu)
        self._tray.activated.connect(self._on_tray_activated)
        self._tray.show()

    # ---------------------------------------------------------------- 语言
    def retranslate(self) -> None:
        """语言切换后的单点扇出：重建主窗口的全部静态文案。

        必须幂等、不触发任何信号；最后调一次 `_refresh()`，让跟数据绑定的
        文案（状态栏、详情面板的值）也跟上。
        """
        self.setWindowTitle(tr(C.APP_NAME))
        self._title.setText(tr(C.APP_NAME))
        self._subtitle.setText(tr("Graphical manager for krfb-virtualmonitor"))
        self._btn_new.setText("  " + tr("New virtual screen"))
        self._btn_start_all.setText(tr("Start all"))
        self._btn_stop_all.setText(tr("Stop all"))
        self._btn_scan.setToolTip(tr("Scan for and adopt krfb processes "
                                     "started outside this app"))
        self._btn_refresh.setToolTip(tr("Refresh now"))
        self._btn_settings.setToolTip(tr("Settings"))
        self._notice.retranslate()
        self._list.retranslate()
        self._detail.retranslate()
        for window in self._log_windows.values():
            window.retranslate()
        if self._tray is not None:
            self._tray.setToolTip(tr(C.APP_NAME))
            self._act_show.setText(tr("Show main window"))
            self._act_start_all.setText(tr("Start all"))
            self._act_stop_all.setText(tr("Stop all"))
            self._act_quit.setText(tr("Quit"))
        app = QApplication.instance()
        if app is not None:
            # 不更新的话：KDE 任务栏/通知里还是旧语言的应用名
            app.setApplicationDisplayName(tr(C.APP_NAME))
        self._refresh()

    # ---------------------------------------------------------------- 数据
    def _items(self) -> list[tuple[Screen, Runtime, ScreenState]]:
        items = []
        for screen in self._store.sorted_screens():
            runtime = self._store.runtime_for(screen.id, create=False)
            state = self._manager.state_of(screen)
            if screen.id in self._pending:
                state = ScreenState.STARTING
            items.append((screen, runtime, state))
        return items

    def _selected_screen(self) -> Screen | None:
        screen_id = self._list.selected_id
        return self._store.get(screen_id) if screen_id else None

    # ---------------------------------------------------------------- 刷新
    def _refresh(self) -> None:
        self._verify_pending()
        items = self._items()

        self._list.sync(items)
        self._check_crashes(items)

        screen = self._selected_screen()
        if screen is None:
            # 没选中就自动选第一个，避免右侧一直空着
            if items:
                self._list.select(items[0][0].id)
                screen = items[0][0]
            else:
                self._detail.clear()

        if screen is not None:
            runtime = self._store.runtime_for(screen.id, create=False)
            state = self._manager.state_of(screen)
            if screen.id in self._pending:
                state = ScreenState.STARTING
            self._detail.update_screen(
                screen, runtime, state, self._secrets.recall(screen.id)
            )

        self._update_status(items)

        running = sum(1 for _, _, state in items if state is ScreenState.RUNNING)
        self._btn_start_all.setEnabled(running < len(items))
        self._btn_stop_all.setEnabled(running > 0)

    def _update_status(self, items) -> None:
        total = len(items)
        running = sum(1 for _, _, s in items if s is ScreenState.RUNNING)
        problem = sum(1 for _, _, s in items if s in (ScreenState.CRASHED, ScreenState.FAILED))

        parts = [trf("{count} virtual screens", count=total),
                 trf("{count} running", count=running)]
        if problem:
            parts.append(trf("{count} need attention", count=problem))
        self._status_left.setText("   ·   ".join(parts))

        status = self._secrets.status
        # 状态文案只有一个来源（SecretsStatus.label），这里不再抄一份
        right = status.label if status is SecretsStatus.OK else f"⚠ {status.label}"
        warnings = self._warnings()
        if warnings:
            right = ("⚠ " + trf("{count} environment problems", count=len(warnings))
                     + "   ·   " + right)
        self._status_right.setText(right)

    def _check_crashes(self, items) -> None:
        """期望运行但进程不在了 —— 用横幅集中提示一次，不重复打扰。"""
        crashed = [
            screen for screen, _, state in items
            if state is ScreenState.CRASHED and screen.id not in self._notified_crash
        ]
        if not crashed:
            return
        for screen in crashed:
            self._notified_crash.add(screen.id)
        self._crashed_now = [s.id for s in crashed]

        self._notice_mode = "crash"
        self._notice.show_message(self._crash_notice_text(), tr("Restart"), "warning",
                                  rebuild=self._crash_notice_payload)

    def _crash_notice_payload(self) -> tuple[str, str]:
        return self._crash_notice_text(), tr("Restart")

    def _crash_notice_text(self) -> str:
        """崩溃横幅文案。从 `_crashed_now` 里的 id 重查名字，语言切换后可以重算。"""
        names = [s.name for s in (self._store.get(i) for i in self._crashed_now) if s]
        if not names:
            return ""
        if len(names) == 1:
            return trf('"{name}" has exited — it may have crashed or been killed',
                       name=names[0])
        return trf("{count} virtual screens have exited ({names}…)",
                   count=len(names), names=join_list(names[:3]))

    # ---------------------------------------------------------------- 验证
    def _verify_pending(self) -> None:
        now = time.monotonic()
        for screen_id in list(self._pending):
            screen = self._store.get(screen_id)
            if screen is None:
                del self._pending[screen_id]
                continue

            runtime = self._store.runtime_for(screen_id, create=False)
            if not self._manager.is_recorded_process_alive(runtime):
                del self._pending[screen_id]
                self._fail(screen, tr("The process exited immediately after starting"))
                continue

            # 先看端口（纯 /proc 读取，几乎零成本），端口起来了再问 KWin。
            # 这样避免每次轮询都走一遍 D-Bus。
            port_up = proctools.port_in_use(screen.port)
            if port_up and self._manager.output_ready(screen):
                del self._pending[screen_id]
                self._manager.apply_requested_scale(screen)
                self._notified_crash.discard(screen_id)
                return  # 列表刷新由下一次 _refresh 接手

            if now > self._pending[screen_id]:
                del self._pending[screen_id]
                detail = (tr(" (the port is listening, but no virtual display was created)")
                          if port_up else tr(" (the port isn't listening either)"))
                self._fail(screen, trf(
                    "Waited {seconds} seconds and the Virtual-{name} output still "
                    "hasn't appeared in KWin{detail}",
                    seconds=int(VERIFY_TIMEOUT_S), name=screen.name, detail=detail,
                ))

    def _fail(self, screen: Screen, reason: str) -> None:
        """判定启动校验失败。

        进程**还活着**时绝不能清运行记录：`mark_stopped` 会把 pid/starttime 抹掉，
        而 `state_of` 只认这两个字段 —— 一清它就成了谁也认不出的孤儿，必须先点
        一次「扫描」才能重新纳管。所以分开：活着只记错误，确实死了才清身份。
        """
        runtime = self._store.runtime_for(screen.id, create=False)
        if self._manager.is_recorded_process_alive(runtime):
            self._store.note_error(screen.id, reason)
        else:
            self._store.mark_stopped(screen.id, error=reason)
        self._show_log_dialog(screen, reason)

    # ---------------------------------------------------------------- 动作
    def _ensure_password(self, screen: Screen) -> str | None:
        """取密码。密钥环不可用时向用户补录，绝不阻塞界面。"""
        password = self._secrets.recall(screen.id)
        if password:
            return password

        try:
            password = self._secrets.get(screen.id)
        except SecretTimeout:
            password = None
        if password:
            return password

        if self._secrets.status is SecretsStatus.OK:
            reason = tr("This virtual screen has no saved password (it may come "
                        "from an old config); enter one now.")
        else:
            reason = self._secrets.detail or self._secrets.status.label
        prompt = PasswordPrompt(
            self._palette, screen.name,
            trf("Cannot read the password from the keyring: {reason}", reason=reason),
            self,
        )
        if prompt.exec():
            password = prompt.password
            self._secrets.set(screen.id, password)
            return password
        return None

    def _on_start(self, screen_id: str) -> None:
        screen = self._store.get(screen_id)
        if screen is None:
            return
        password = self._ensure_password(screen)
        if password is None:
            return

        result = self._manager.spawn(screen, password)
        if not result.ok:
            self._store.mark_stopped(screen.id, error=result.error)
            self._show_log_dialog(screen, result.error)
            self._refresh()
            return

        self._pending[screen.id] = time.monotonic() + VERIFY_TIMEOUT_S
        self._refresh()

    def _on_stop(self, screen_id: str) -> None:
        screen = self._store.get(screen_id)
        if screen is None:
            return
        self._pending.pop(screen_id, None)
        self._manager.terminate(screen)
        # 给进程一点时间退出，随后由轮询更新状态
        QTimer.singleShot(700, self._refresh)

    def _on_start_all(self) -> None:
        targets = [
            s for s in self._store.sorted_screens()
            if self._manager.state_of(s) is not ScreenState.RUNNING
        ]
        for screen in targets:
            self._on_start(screen.id)

    def _on_stop_all(self) -> None:
        for screen in self._store.sorted_screens():
            if screen.id in self._pending or self._manager.state_of(screen) is ScreenState.RUNNING:
                self._on_stop(screen.id)

    def _on_new(self) -> None:
        dialog = ScreenDialog(self._palette, self._store, None, None, self)
        if not dialog.exec():
            return
        screen = dialog.result_screen
        if screen is None:
            return
        self._store.add(screen)
        self._secrets.set(screen.id, dialog.result_password)
        self._list.select(screen.id)
        self._refresh()
        # 新建后直接启动，符合"建了就是要用"的直觉
        self._on_start(screen.id)

    def _on_edit(self, screen_id: str) -> None:
        screen = self._store.get(screen_id)
        if screen is None:
            return
        running = self._manager.state_of(screen) is ScreenState.RUNNING
        dialog = ScreenDialog(
            self._palette, self._store, screen,
            self._secrets.recall(screen_id) or self._secrets.get(screen_id),
            self,
        )
        if not dialog.exec():
            return
        updated = dialog.result_screen
        if updated is None:
            return
        old_port = screen.port
        self._store.save_screens()
        self._secrets.set(updated.id, dialog.result_password)

        if running and (old_port != updated.port
                        or updated.width != screen.width
                        or updated.height != screen.height
                        or abs(updated.scale - screen.scale) > 1e-6):
            # 自建而不是用 QMessageBox.question：标准按钮的文案要显式设成本程序
            # 的语言（Qt 自带的 qtbase_*.qm 不随本程序分发）
            box = QMessageBox(self)
            box.setWindowTitle(tr("Restart required"))
            box.setIcon(QMessageBox.Icon.Question)
            box.setText(trf(
                '"{name}" is running. Changes to the resolution, scale or port '
                "do not affect a screen that has already been created; the "
                "virtual screen must be restarted for them to take effect.",
                name=updated.name,
            ))
            box.setInformativeText(tr("Restart it now?"))
            box.setStandardButtons(
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            box.button(QMessageBox.StandardButton.Yes).setText(tr("Restart now"))
            box.button(QMessageBox.StandardButton.No).setText(tr("Later"))
            if box.exec() == QMessageBox.StandardButton.Yes:
                self._on_stop(updated.id)
                QTimer.singleShot(1200, lambda: self._on_start(updated.id))
        self._refresh()

    def _on_delete(self, screen_id: str) -> None:
        screen = self._store.get(screen_id)
        if screen is None:
            return

        running = self._manager.state_of(screen) is ScreenState.RUNNING
        detail = (tr("This virtual screen is currently running; deleting it will "
                     "stop it first.") if running else tr("This action cannot be undone."))
        box = QMessageBox(self)
        box.setWindowTitle(tr("Delete virtual screen"))
        box.setIcon(QMessageBox.Icon.Warning)
        box.setText(trf('Delete "{name}"?', name=screen.name))
        box.setInformativeText(detail + "\n"
                               + tr("The saved password is removed from the keyring too."))
        box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel)
        box.button(QMessageBox.StandardButton.Yes).setText(tr("Delete"))
        box.button(QMessageBox.StandardButton.Cancel).setText(tr("Cancel"))
        if box.exec() != QMessageBox.StandardButton.Yes:
            return

        if running:
            self._manager.terminate(screen)

        window = self._log_windows.pop(screen_id, None)
        if window is not None:
            window.close()

        self._secrets.delete(screen_id)
        self._store.remove(screen_id)
        self._notified_crash.discard(screen_id)
        self._list.select(None)
        self._detail.clear()
        self._refresh()

    def _on_scan(self) -> None:
        candidates = self._manager.unmanaged_processes()
        if not candidates:
            self._notice_mode = "info"
            self._notice.show_message(
                tr("No unmanaged krfb processes found"), "", "accent",
                rebuild=lambda: (tr("No unmanaged krfb processes found"), ""),
            )
            QTimer.singleShot(3200, self._notice.fade_out)
            return

        dialog = AdoptDialog(self._palette, candidates, self)
        if not dialog.exec():
            return

        adopted, failures = [], []
        for info in dialog.selected:
            screen, error = self._manager.adopt(info)
            if screen is not None:
                adopted.append(screen)
            else:
                failures.append(trf("{name}: {error}", name=info.name, error=error))

        if adopted:
            self._list.select(adopted[0].id)
        if failures:
            QMessageBox.warning(self, tr("Some could not be imported"),
                                "\n".join(failures))
        self._refresh()

    def _on_log(self, screen_id: str) -> None:
        screen = self._store.get(screen_id)
        if screen is None:
            return
        window = self._log_windows.get(screen_id)
        if window is None:
            window = LogViewer(
                self._palette, screen.name, self._manager.log_path(screen_id), self
            )
            self._log_windows[screen_id] = window
        window.show()
        window.raise_()
        window.activateWindow()

    def _show_log_dialog(self, screen: Screen, reason: str) -> None:
        """启动失败时把日志尾部一并呈现 —— portal/Wayland 类错误的线索都在里面。"""
        tail = self._manager.read_log_tail(screen.id)
        box = QMessageBox(self)
        box.setWindowTitle(tr("Start failed"))
        box.setIcon(QMessageBox.Icon.Warning)
        box.setText(trf('"{name}" failed to start', name=screen.name))
        box.setInformativeText(reason)
        if tail.strip():
            # 注意：setDetailedText 会让 Qt 自己造一个 "Show Details…" 按钮，
            # 那个文案不归本程序的词条管（Qt 自带的 .qm 不随本程序分发），
            # 在英文之外会保持英文 —— 可发现路径是下面这个自定义按钮。
            box.setDetailedText(tail)
        box.setStandardButtons(QMessageBox.StandardButton.Ok)
        box.button(QMessageBox.StandardButton.Ok).setText(tr("Close"))
        show_log = box.addButton(tr("View full log"), QMessageBox.ButtonRole.ActionRole)
        box.exec()
        if box.clickedButton() is show_log:
            self._on_log(screen.id)

    def _on_settings(self) -> None:
        dialog = SettingsDialog(
            self._palette,
            # provider 而不是快照：语言切换后要重新拼一遍（文案是成品字符串）
            lambda: self._warnings(force=True),
            self._secrets.status, self._secrets.status_detail,
            self._krfb_version_source(), self,
        )
        dialog._unlock.clicked.connect(lambda: self._on_unlock(dialog))
        dialog.exec()
        # 无条件重刷：语言可能刚在对话框里被改过。retranslate 幂等且便宜。
        self.retranslate()

    def _on_unlock(self, dialog: SettingsDialog) -> None:
        """设置里的"解锁密钥环"。同样走后台：系统提示框可能等上几十秒，
        同步调用会把界面冻住。结果由 _on_unlock_finished 弹框反馈。"""
        self._secrets.probe()
        dialog.accept()
        if self._secrets.status is not SecretsStatus.LOCKED:
            # 点按钮之前密钥环已经被解开了（比如用户在系统托盘里解过）
            QMessageBox.information(self, tr("Keyring"), tr("Keyring ready"))
            self._refresh()
            return
        self._request_unlock(automatic=False)

    def _krfb_version_source(self) -> str:
        """返回**源字符串**：真实版号不是词条会原样透传，`not installed` /
        `unknown` 是词条，由设置对话框按当前语言渲染。"""
        binary = proctools.krfb_binary()
        if binary is None:
            return "not installed"
        # 必须走清洗过的环境：打包版里它同样会 abort，而下面的 (stdout or stderr)
        # 兜底会把 Qt 的报错行当成版号显示出来。
        proc = envtools.run_helper([binary, "--version"], timeout=4)
        if proc is None or proc.returncode != 0:
            return "unknown"
        first = (proc.stdout or proc.stderr).strip().splitlines()
        return first[0] if first else "unknown"

    # ---------------------------------------------------------------- 通知条
    def _on_notice_action(self) -> None:
        self._notice.fade_out()
        if self._notice_mode == "env":
            self._on_settings()
            return
        targets = list(self._crashed_now)
        self._crashed_now = []
        for screen_id in targets:
            self._on_start(screen_id)

    def _on_notice_closed(self) -> None:
        self._crashed_now = []
        self._notice.fade_out()

    # ---------------------------------------------------------------- 其它
    def _on_selection(self, screen_id: str) -> None:
        self._refresh()

    def _on_row_activated(self, screen_id: str) -> None:
        screen = self._store.get(screen_id)
        if screen is None:
            return
        if self._manager.state_of(screen) is ScreenState.RUNNING:
            self._on_log(screen_id)
        else:
            self._on_start(screen_id)

    def _env_notice_payload(self) -> tuple[str, str]:
        text = trf("{count} environment problems detected", count=len(self._warnings()))
        return text, tr("View")

    def _startup_report(self, start_in_tray: bool) -> None:
        # 密钥环锁着就主动申请解锁：不申请的话读不到已保存的密码，
        # 每个虚拟屏都得让用户重新手输一遍。后台跑，不挡启动。
        self._request_unlock(automatic=True)

        if self._warnings():
            self._notice_mode = "env"
            self._notice.show_message(*self._env_notice_payload(), "warning",
                                      rebuild=self._env_notice_payload)

        if start_in_tray:
            # 由开机自启拉起：恢复所有"期望运行"的虚拟屏，并缩到托盘
            if self._unlock_running:
                # 正在等用户解锁 → 解锁完再启动，否则密码读不到、起了也起不来
                self._pending_start_all = True
            else:
                QTimer.singleShot(400, self._on_start_all)
            QTimer.singleShot(900, self.hide)

    def _show_window(self) -> None:
        self.show()
        self.raise_()
        self.activateWindow()

    def _on_tray_activated(self, reason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.isVisible():
                self.hide()
            else:
                self._show_window()

    def _quit(self) -> None:
        self._really_quit = True
        self.close()  # 收尾与退出都在 closeEvent 里，那里是唯一的出口

    def _minimize_to_tray(self) -> None:
        self.hide()
        self._clock.pause()
        if not self._tray_hint_shown:
            self._tray_hint_shown = True
            self._tray.showMessage(
                tr(C.APP_NAME),
                tr("Minimized to the tray. Virtual screens keep running and "
                   "are not stopped when you quit this app."),
                icons.app_icon(), 4000,
            )

    def _ask_close_action(self) -> str | None:
        """点关闭按钮时的询问弹窗。返回 `tray` / `quit`；用户取消返回 None。"""
        box = QMessageBox(self)
        box.setWindowTitle(tr(C.APP_NAME))
        box.setIcon(QMessageBox.Icon.Question)
        box.setText(tr("Close the window or minimize to the tray?"))
        tray_button = box.addButton(tr("Minimize to tray"),
                                    QMessageBox.ButtonRole.AcceptRole)
        quit_button = box.addButton(tr("Quit the program"),
                                    QMessageBox.ButtonRole.DestructiveRole)
        box.addButton(tr("Cancel"), QMessageBox.ButtonRole.RejectRole)
        remember = QCheckBox(tr("Remember my choice"))
        box.setCheckBox(remember)
        # 默认落在"最小化"上：回车或手滑不该把管理界面关掉
        box.setDefaultButton(tray_button)
        box.exec()

        clicked = box.clickedButton()
        if clicked is tray_button:
            action = prefs.CLOSE_TRAY
        elif clicked is quit_button:
            action = prefs.CLOSE_QUIT
        else:
            return None
        if remember.isChecked():
            # 写盘失败不打断：本次选择照样生效，只是下次还得再选一遍
            prefs.set_close_action(action)
        return action

    def _shutdown(self) -> None:
        """真正退出前的收尾：停轮询、关日志窗口、摘掉托盘图标。"""
        self._timer.stop()
        self._clock.pause()
        for window in self._log_windows.values():
            window.close()
        if self._tray is not None:
            self._tray.hide()

    def closeEvent(self, event) -> None:  # noqa: N802
        """关闭窗口按设置来：缩到托盘、退出，或者每次问一遍。

        窗口关闭 ≠ 程序退出 —— 虚拟屏在独立会话里继续跑，本程序只是管理界面。
        """
        if self._tray is not None and not self._really_quit:
            action = prefs.close_action()
            if action == prefs.CLOSE_ASK:
                action = self._ask_close_action()
            if action is None:            # 在询问里取消了，窗口保持打开
                event.ignore()
                return
            if action == prefs.CLOSE_TRAY:
                event.ignore()
                self._minimize_to_tray()
                return

        # 走到这里就是真要退出。必须显式调 quit()：main.py 设了
        # quitOnLastWindowClosed=False（托盘模式需要它），只关窗口的话进程会
        # 无声无息地留在后台。
        self._shutdown()
        super().closeEvent(event)
        QApplication.quit()

    def showEvent(self, event) -> None:  # noqa: N802
        self._clock.set_active(True)
        super().showEvent(event)

    def hideEvent(self, event) -> None:  # noqa: N802
        self._clock.set_active(False)
        super().hideEvent(event)
