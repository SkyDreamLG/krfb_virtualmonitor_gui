"""右侧详情面板。

有一个设计上的坚持：**请求值与实际生效值分开显示**。实测 `--scale` 会被 KWin
覆写（请求 1.25/1.5 都变成 1.75），如果界面只显示请求值，就是在骗用户。
"""

from __future__ import annotations

import socket
from typing import Callable

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ..i18n import tr, trf
from ..models import Runtime, Screen, ScreenState
from . import icons
from .screen_list import state_color
from .theme import Palette
from .vector import AspectPreview


def local_address() -> str:
    """本机名，用作 VNC 连接地址。失败时退回 localhost。"""
    try:
        return socket.gethostname() or "localhost"
    except OSError:
        return "localhost"


class CopyButton(QPushButton):
    """复制到剪贴板的图标按钮，点击后短暂变成对勾反馈。

    tooltip 传**零参 provider** 而不是成品字符串：语言切换后 retranslate()
    才能重算，且英文原文留在调用点，静态扫描看得到。
    """

    def __init__(self, palette: Palette, get_text, tooltip: Callable[[], str],
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._palette = palette
        self._get_text = get_text
        self._base_tooltip = tooltip
        self._copied = False
        self.setFlat(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        icons.mark_icon_only(self)
        self.setFixedSize(26, 26)
        self.setIcon(icons.icon("copy", palette.color("text_dim"), 15))
        self.setToolTip(tooltip())
        self.setStyleSheet("QPushButton{border:none;background:transparent;}"
                           "QPushButton:hover{background:transparent;}")
        self.clicked.connect(self._copy)

    def _copy(self) -> None:
        text = self._get_text()
        if not text:
            return
        QApplication.clipboard().setText(text)
        self.setIcon(icons.icon("check", self._palette.color("success"), 15))
        self._copied = True
        self.setToolTip(tr("Copied"))
        # 1.1 秒后恢复，用 QTimer 而不是动画 —— 这里只需要一个状态翻转
        from PySide6.QtCore import QTimer

        QTimer.singleShot(1100, self._restore)

    def _restore(self) -> None:
        self.setIcon(icons.icon("copy", self._palette.color("text_dim"), 15))
        self._copied = False
        self.setToolTip(self._base_tooltip())

    def retranslate(self) -> None:
        self.setToolTip(tr("Copied") if self._copied else self._base_tooltip())


class InfoRow(QWidget):
    """一行"标签 + 值"。标签同样用零参 provider，见 CopyButton。"""

    def __init__(self, palette: Palette, label: Callable[[], str],
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._palette = palette
        self._label_provider = label

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self._label = QLabel(label())
        self._label.setFixedWidth(66)
        self._label.setProperty("role", "dim")

        self._value = QLabel("—")
        self._value.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self._value.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self._value.setWordWrap(True)

        layout.addWidget(self._label)
        layout.addWidget(self._value, 1)

    def set_value(self, text: str, *, color: str | None = None,
                  mono: bool = False, tooltip: str = "") -> None:
        self._value.setText(text)
        font: QFont = self._value.font()
        font.setFamilies(["JetBrains Mono", "DejaVu Sans Mono", "monospace"] if mono
                         else self.font().families())
        self._value.setFont(font)
        self._value.setStyleSheet(
            f"color: {self._palette.color(color).name()};" if color else ""
        )
        self._value.setToolTip(tooltip)

    def add_widget(self, widget: QWidget) -> None:
        self.layout().addWidget(widget)

    def retranslate(self) -> None:
        self._label.setText(self._label_provider())


class DetailPane(QWidget):
    """详情面板：没选中时显示引导语，选中后显示全部信息与操作。"""

    start_requested = Signal(str)
    stop_requested = Signal(str)
    edit_requested = Signal(str)
    log_requested = Signal(str)
    delete_requested = Signal(str)

    def __init__(self, palette: Palette, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._palette = palette
        self._screen: Screen | None = None
        self._state = ScreenState.STOPPED
        # 缓存最后一次 update_screen 的运行态，retranslate() 时原样重放
        self._runtime = Runtime()

        self._scroll = QScrollArea(self)
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)

        self._content = QWidget()
        self._scroll.setWidget(self._content)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self._scroll)

        # --- 空状态 ---
        self._empty = QWidget()
        empty_layout = QVBoxLayout(self._empty)
        empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.setSpacing(6)
        self._empty_hint = QLabel(tr("Select a virtual screen on the left"))
        self._empty_hint.setProperty("role", "dim")
        self._empty_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_sub = QLabel(tr("or click \"New\" in the top right"))
        self._empty_sub.setProperty("role", "faint")
        self._empty_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(self._empty_hint)
        empty_layout.addWidget(self._empty_sub)

        # --- 正常内容 ---
        self._body = QWidget()
        body = QVBoxLayout(self._body)
        body.setContentsMargins(22, 20, 22, 18)
        body.setSpacing(14)

        # 标题 + 状态徽标
        head = QHBoxLayout()
        head.setSpacing(10)
        self._title = QLabel("—")
        self._title.setProperty("role", "h1")
        self._title.setWordWrap(True)
        self._badge = QLabel("")
        self._badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        head.addWidget(self._title, 1)
        head.addWidget(self._badge, 0, Qt.AlignmentFlag.AlignTop)
        body.addLayout(head)

        # 矢量分辨率预览
        self._preview = AspectPreview(palette, self._body)
        body.addWidget(self._preview)

        # 信息行
        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setVerticalSpacing(9)

        self._row_requested = InfoRow(palette, lambda: tr("Requested"))
        self._row_actual = InfoRow(palette, lambda: tr("Actual"))
        self._row_port = InfoRow(palette, lambda: tr("Port"))
        self._row_address = InfoRow(palette, lambda: tr("Address"))
        self._row_status = InfoRow(palette, lambda: tr("Status"))
        self._row_notes = InfoRow(palette, lambda: tr("Notes"))

        self._copy_address = CopyButton(palette, lambda: self._address_text,
                                        lambda: tr("Copy the VNC address"))
        self._row_address.add_widget(self._copy_address)

        self._copy_password = CopyButton(palette, lambda: self._password_text,
                                         lambda: tr("Copy the connection password"))
        self._row_password = InfoRow(palette, lambda: tr("Password"))
        self._row_password.add_widget(self._copy_password)

        self._rows = (self._row_requested, self._row_actual, self._row_port,
                      self._row_address, self._row_password, self._row_status,
                      self._row_notes)
        for index, row in enumerate(self._rows):
            grid.addWidget(row, index, 0)
        body.addLayout(grid)

        body.addStretch(1)

        # 操作按钮
        actions = QHBoxLayout()
        actions.setSpacing(8)
        self._btn_toggle = QPushButton(tr("Start"))
        self._btn_toggle.setProperty("accent", True)
        self._btn_edit = QPushButton(tr("Edit"))
        self._btn_log = QPushButton(tr("Log"))
        self._btn_delete = QPushButton(tr("Delete"))
        self._btn_delete.setProperty("danger", True)

        self._btn_toggle.clicked.connect(self._on_toggle)
        self._btn_edit.clicked.connect(lambda: self._emit(self.edit_requested))
        self._btn_log.clicked.connect(lambda: self._emit(self.log_requested))
        self._btn_delete.clicked.connect(lambda: self._emit(self.delete_requested))

        for button in (self._btn_toggle, self._btn_edit, self._btn_log):
            actions.addWidget(button)
        actions.addStretch(1)
        actions.addWidget(self._btn_delete)
        body.addLayout(actions)

        root = QVBoxLayout(self._content)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(self._empty)
        root.addWidget(self._body)
        self._body.hide()

        self._address_text = ""
        self._password_text = ""

    # --- 内部 ---------------------------------------------------------------
    def _emit(self, signal) -> None:
        if self._screen is not None:
            signal.emit(self._screen.id)

    def _on_toggle(self) -> None:
        if self._screen is None:
            return
        if self._state in (ScreenState.RUNNING, ScreenState.STARTING):
            self.stop_requested.emit(self._screen.id)
        else:
            self.start_requested.emit(self._screen.id)

    def _set_badge(self, text: str, color: QColor) -> None:
        base = color.name()
        bg = f"rgba({color.red()},{color.green()},{color.blue()},0.16)"
        self._badge.setText(text)
        self._badge.setStyleSheet(
            f"QLabel{{color:{base}; background:{bg}; border:1px solid {base};"
            f"border-radius:9px; padding:2px 10px; font-weight:600; font-size:12px;}}"
        )

    # --- 对外 ---------------------------------------------------------------
    def clear(self) -> None:
        self._screen = None
        self._body.hide()
        self._empty.show()

    def retranslate(self) -> None:
        """语言切换后重建全部静态文案。选中的屏幕若有则整体重放一遍
        update_screen，避免静态部分和动态部分走两条会分叉的路径。"""
        self._empty_hint.setText(tr("Select a virtual screen on the left"))
        self._empty_sub.setText(tr("or click \"New\" in the top right"))
        for row in self._rows:
            row.retranslate()
        self._copy_address.retranslate()
        self._copy_password.retranslate()
        if self._screen is not None:
            self.update_screen(self._screen, self._runtime, self._state,
                               self._password_text or None)
        else:
            # 没选中任何屏幕时按钮文字也要跟着语言走（此时不经过 update_screen）
            self._apply_actions()

    def update_screen(self, screen: Screen | None, runtime: Runtime,
                      state: ScreenState, password: str | None) -> None:
        if screen is None:
            self.clear()
            return

        self._screen = screen
        self._state = state
        self._runtime = runtime
        self._empty.hide()
        self._body.show()

        self._title.setText(screen.name)
        color = state_color(self._palette, state)
        self._set_badge(f"● {state.label}", color)

        # 预览：运行中优先显示实测值，并标出被覆写的缩放
        overridden = state.is_active and runtime.scale_overridden(screen.scale)
        if state.is_active and runtime.actual_width and runtime.actual_height:
            self._preview.set_resolution(
                runtime.actual_width, runtime.actual_height,
                f"{runtime.actual_resolution_display}",
                f"@{runtime.actual_scale:g}x" if runtime.actual_scale else "",
            )
        else:
            self._preview.set_resolution(
                screen.width, screen.height,
                screen.resolution_display, f"@{screen.scale:g}x",
            )
        self._preview.set_warning(overridden)

        self._row_requested.set_value(f"{screen.resolution_display} @ {screen.scale:g}x", mono=True)
        self._row_requested.show()

        if state.is_active and runtime.actual_scale is not None:
            actual = f"{runtime.actual_resolution_display} @ {runtime.actual_scale:g}x"
            if overridden:
                self._row_actual.set_value(
                    trf("{actual}  ⚠ differs from the requested value", actual=actual),
                    color="warning", mono=True,
                )
            else:
                self._row_actual.set_value(f"{actual}  ✓", color="success", mono=True)
            self._row_actual.show()
        else:
            self._row_actual.hide()

        self._row_port.set_value(str(screen.port), mono=True)

        self._address_text = f"vnc://{local_address()}:{screen.port}"
        self._row_address.set_value(self._address_text, mono=True)

        if password:
            self._password_text = password
            self._row_password.set_value(
                "•" * len(password), mono=True,
                tooltip=tr("The password is only hidden in the UI; "
                           "it is passed to krfb in plain text"),
            )
            self._row_password.show()
        else:
            self._password_text = ""
            self._row_password.hide()

        if state is ScreenState.RUNNING:
            self._row_status.set_value(
                trf("Running, PID {pid}", pid=runtime.pid),
                color="success", mono=True,
            )
        elif state is ScreenState.CRASHED:
            self._row_status.set_value(
                tr("Process is gone but marked as \"desired running\""),
                color="warning",
                tooltip=runtime.last_error or tr(
                    "It may have crashed, been killed, or the machine was rebooted"
                ),
            )
        elif state is ScreenState.FAILED:
            self._row_status.set_value(
                runtime.last_error or tr("Failed to start"), color="danger",
            )
        elif state is ScreenState.STARTING:
            self._row_status.set_value(tr("Creating, waiting for the KWin output…"),
                                       color="accent")
        else:
            self._row_status.set_value(tr("Stopped"))

        self._row_notes.set_value(screen.notes or "—",
                                  color=None if screen.notes else "text_faint")

        self._apply_actions()

    def _apply_actions(self) -> None:
        """操作按钮的文字、图标与提示。只依赖 `self._state`，所以 update_screen
        和 retranslate 都走这里 —— 没选中屏幕时按钮也必须跟着语言变。"""
        running = self._state in (ScreenState.RUNNING, ScreenState.STARTING)
        self._btn_toggle.setText(tr("Stop") if running else tr("Start"))
        # 这个按钮是 accent 样式（白字），图标也用白色
        self._btn_toggle.setIcon(
            icons.icon("stop" if running else "play", "#ffffff", 14)
        )
        self._btn_edit.setText(tr("Edit"))
        self._btn_log.setText(tr("Log"))
        self._btn_delete.setText(tr("Delete"))
        self._btn_edit.setIcon(icons.icon("edit", self._palette.color("text"), 14))
        self._btn_log.setIcon(icons.icon("log", self._palette.color("text"), 14))
        self._btn_delete.setIcon(icons.icon("trash", self._palette.color("danger"), 14))
        # 运行中改分辨率/缩放对已建成的输出无效，所以编辑按钮要提示
        self._btn_edit.setToolTip(
            tr("Changing resolution or scale while running has no effect on the "
               "created screen; the virtual screen must be restarted")
            if running else tr("Edit parameters")
        )
