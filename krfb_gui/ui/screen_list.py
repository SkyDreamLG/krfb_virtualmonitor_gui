"""左侧虚拟屏列表。

行是**完全自绘**的，不用 QGraphicsOpacityEffect —— 效果器会走离屏 pixmap，
在列表视口里会产生重绘瑕疵，而且一个控件只能挂一个效果器，没法同时做
hover 高光和进出场淡入。

进出场动画通过插值 `setFixedHeight` 实现，而不是动画 `maximumHeight`：
后者会被布局的最小高度钳住，而且如果结束值小于 sizeHint 会永久裁切内容。
"""

from __future__ import annotations

from PySide6.QtCore import (
    Property,
    QEasingCurve,
    QPropertyAnimation,
    QRectF,
    Qt,
    Signal,
)
from PySide6.QtGui import QColor, QFont, QFontMetrics, QPainter, QPen
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ..i18n import tr, trf
from ..models import Runtime, Screen, ScreenState
from .theme import Palette, font_at, with_alpha
from .vector import Clock, StatusDot

ROW_HEIGHT = 62
ROW_SPACING = 3


def state_color(palette: Palette, state: ScreenState) -> QColor:
    """状态 → 颜色。集中在一处，列表和详情页共用，保证语义一致。"""
    return {
        ScreenState.RUNNING: palette.color("success"),
        ScreenState.STARTING: palette.color("accent"),
        ScreenState.STOPPED: palette.color("text_faint"),
        ScreenState.CRASHED: palette.color("warning"),
        ScreenState.FAILED: palette.color("danger"),
        ScreenState.UNMANAGED: palette.color("accent"),
    }[state]


class ScreenRow(QWidget):
    """列表中的一行。自绘 + 单个 StatusDot 子控件。"""

    clicked = Signal(str)
    double_clicked = Signal(str)

    def __init__(self, screen: Screen, palette: Palette, clock: Clock,
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._palette = palette
        self._screen = screen
        self._runtime = Runtime()
        self._state = ScreenState.STOPPED
        self._selected = False
        self._hover_t = 0.0
        self._appear = 0.0
        self._collapse = 1.0

        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(ROW_HEIGHT)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self._dot = StatusDot(clock, palette, diameter=24, parent=self)
        self._dot.move(11, (ROW_HEIGHT - 24) // 2)

        self._hover_anim = QPropertyAnimation(self, b"hoverT", self)
        self._hover_anim.setDuration(150)
        self._hover_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._appear_anim = QPropertyAnimation(self, b"appearT", self)
        self._appear_anim.setDuration(260)
        self._appear_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._appear_anim.setStartValue(0.0)
        self._appear_anim.setEndValue(1.0)
        self._appear_anim.start()

        self._collapse_anim = QPropertyAnimation(self, b"collapseT", self)
        self._collapse_anim.setDuration(200)
        self._collapse_anim.setEasingCurve(QEasingCurve.Type.InCubic)

    # --- 动画属性 -----------------------------------------------------------
    def _get_hover(self) -> float:
        return self._hover_t

    def _set_hover(self, value: float) -> None:
        self._hover_t = float(value)
        self.update()

    hoverT = Property(float, _get_hover, _set_hover)

    def _get_appear(self) -> float:
        return self._appear

    def _set_appear(self, value: float) -> None:
        self._appear = float(value)
        self.update()

    appearT = Property(float, _get_appear, _set_appear)

    def _get_collapse(self) -> float:
        return self._collapse

    def _set_collapse(self, value: float) -> None:
        self._collapse = float(value)
        self.setFixedHeight(max(0, int(ROW_HEIGHT * self._collapse)))
        self.update()

    collapseT = Property(float, _get_collapse, _set_collapse)

    # --- 数据 ---------------------------------------------------------------
    @property
    def screen_id(self) -> str:
        return self._screen.id

    def update_data(self, screen: Screen, runtime: Runtime, state: ScreenState) -> None:
        self._screen = screen
        self._runtime = runtime
        self._state = state
        self._dot.set_state(state_color(self._palette, state), state.is_active)
        self.retranslate()
        self.update()

    def retranslate(self) -> None:
        """语言切换后重设文案。行是自绘的，`state.label` 在 paintEvent 里现查，
        但没人保证切换后会发生重绘 —— 所以这里显式 update()。"""
        self.setToolTip(trf("{name}\n{resolution} · Port {port}",
                            name=self._screen.name,
                            resolution=self._screen.resolution,
                            port=self._screen.port))
        self.update()

    def set_selected(self, selected: bool) -> None:
        if selected != self._selected:
            self._selected = selected
            self.update()

    def animate_out(self, on_done) -> None:
        """移除前的收起动画。没有这个的话，列表会突然塌一块。"""
        self._collapse_anim.stop()
        self._collapse_anim.setStartValue(self._collapse)
        self._collapse_anim.setEndValue(0.0)
        try:
            self._collapse_anim.finished.disconnect()
        except (RuntimeError, TypeError):
            pass
        self._collapse_anim.finished.connect(on_done)
        self._collapse_anim.start()

    # --- 交互 ---------------------------------------------------------------
    def enterEvent(self, event) -> None:  # noqa: N802
        self._animate_hover(1.0)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:  # noqa: N802
        self._animate_hover(0.0)
        super().leaveEvent(event)

    def _animate_hover(self, target: float) -> None:
        self._hover_anim.stop()
        self._hover_anim.setStartValue(self._hover_t)
        self._hover_anim.setEndValue(target)
        self._hover_anim.start()

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self._screen.id)
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self.double_clicked.emit(self._screen.id)
        super().mouseDoubleClickEvent(event)

    def resizeEvent(self, event) -> None:  # noqa: N802
        self._dot.move(11, (self.height() - self._dot.height()) // 2)
        super().resizeEvent(event)

    # --- 绘制 ---------------------------------------------------------------
    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        # 出场淡出 + 进场淡入，都是直接乘 alpha，不用效果器
        painter.setOpacity(max(0.0, min(1.0, self._appear * self._collapse)))

        rect = QRectF(self.rect()).adjusted(3, 1, -3, -1)
        accent = self._palette.color("accent")

        if self._selected:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(self._palette.alpha("accent", 0.16))
            painter.drawRoundedRect(rect, 9, 9)
            # 左侧选中指示条
            painter.setBrush(accent)
            painter.drawRoundedRect(QRectF(rect.left(), rect.top() + 9, 2.5, rect.height() - 18), 1.25, 1.25)
        elif self._hover_t > 0.001:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(with_alpha(
                self._palette.color("surface_hover"), 0.9 * self._hover_t
            ))
            painter.drawRoundedRect(rect, 9, 9)

        text_left = 46
        right_pad = 10
        available = self.width() - text_left - right_pad
        if available <= 20:
            return

        color = state_color(self._palette, self._state)

        # 第一行：名称 + 状态
        name_font = font_at(self.font(), 0.5, bold=True)
        name_metrics = QFontMetrics(name_font)

        state_font = font_at(self.font(), -1.5)
        state_metrics = QFontMetrics(state_font)
        state_text = self._state.label
        state_width = state_metrics.horizontalAdvance(state_text)

        name_width = max(20, available - state_width - 8)
        name_text = name_metrics.elidedText(self._screen.name, Qt.TextElideMode.ElideRight, name_width)

        painter.setFont(name_font)
        painter.setPen(self._palette.color("text"))
        painter.drawText(QRectF(text_left, 11, name_width, name_metrics.height()),
                         Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, name_text)

        painter.setFont(state_font)
        painter.setPen(color)
        painter.drawText(
            QRectF(self.width() - right_pad - state_width, 11, state_width, name_metrics.height()),
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, state_text,
        )

        # 第二行：分辨率 · 端口（运行中优先显示实测值）
        meta_font = font_at(self.font(), -1.5)
        meta_metrics = QFontMetrics(meta_font)
        painter.setFont(meta_font)

        actual = self._runtime.actual_resolution_display
        if self._state.is_active and actual:
            meta = f"{actual}"
            if self._runtime.actual_scale is not None:
                meta += f" @{self._runtime.actual_scale:g}x"
            meta += f" · :{self._screen.port}"
        else:
            meta = f"{self._screen.resolution_display} @{self._screen.scale:g}x · :{self._screen.port}"

        painter.setPen(self._palette.color("text_dim"))
        painter.drawText(
            QRectF(text_left, 31, available, meta_metrics.height()),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            meta_metrics.elidedText(meta, Qt.TextElideMode.ElideRight, available),
        )

        # 缩放的请求值与实际值不符时，给一个不打扰的提示点
        if (self._state.is_active
                and self._runtime.scale_overridden(self._screen.scale)):
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(self._palette.color("warning"))
            painter.drawEllipse(QRectF(self.width() - right_pad - 5, 34, 5, 5))


class ScreenList(QWidget):
    """列表容器。刷新时做**增量更新**，不重建全部行 —— 重建会打断动画和 hover 状态。"""

    selection_changed = Signal(str)
    row_activated = Signal(str)

    def __init__(self, palette: Palette, clock: Clock, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._palette = palette
        self._clock = clock
        self._rows: dict[str, ScreenRow] = {}
        self._selected: str | None = None
        self._pending_removal: set[str] = set()

        self._scroll = QScrollArea(self)
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)

        self._container = QWidget()
        self._layout = QVBoxLayout(self._container)
        self._layout.setContentsMargins(6, 6, 6, 6)
        self._layout.setSpacing(ROW_SPACING)
        self._layout.addStretch(1)
        self._scroll.setWidget(self._container)

        # 空状态提示
        # 侧栏只有 232px 宽，且这行不换行 —— 英文必须短到放得下
        self._empty = QLabel(tr("No virtual screens yet\n"
                                "Click \"New\" to create one"))
        self._empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty.setProperty("role", "faint")
        self._empty.setParent(self)
        self._empty.hide()

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self._scroll)

    def resizeEvent(self, event) -> None:  # noqa: N802
        self._empty.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)

    @property
    def rows(self) -> dict[str, ScreenRow]:
        return self._rows

    @property
    def selected_id(self) -> str | None:
        return self._selected

    def retranslate(self) -> None:
        self._empty.setText(tr("No virtual screens yet\n"
                               "Click \"New\" to create one"))
        for row in self._rows.values():
            row.retranslate()

    def select(self, screen_id: str | None) -> None:
        if screen_id == self._selected:
            return
        self._selected = screen_id
        for key, row in self._rows.items():
            row.set_selected(key == screen_id)
        if screen_id is not None:
            self.selection_changed.emit(screen_id)

    def sync(self, items: list[tuple[Screen, Runtime, ScreenState]]) -> None:
        """把列表内容对齐到给定数据，尽量复用已有行。"""
        wanted = {screen.id for screen, _, _ in items}

        # 移除已消失的（带动画）
        for screen_id in list(self._rows):
            if screen_id not in wanted and screen_id not in self._pending_removal:
                self._remove_row(screen_id)

        # 新增或就地更新
        for index, (screen, runtime, state) in enumerate(items):
            row = self._rows.get(screen.id)
            if row is None:
                row = ScreenRow(screen, self._palette, self._clock, self._container)
                row.clicked.connect(self.select)
                row.double_clicked.connect(self.row_activated)
                row.set_selected(screen.id == self._selected)
                self._layout.insertWidget(index, row)
                # 插入时也启动淡入，避免"凭空出现"
                row._appear_anim.start()
                self._rows[screen.id] = row
            row.update_data(screen, runtime, state)

            current_index = self._layout.indexOf(row)
            if current_index != index:
                self._layout.removeWidget(row)
                self._layout.insertWidget(index, row)

        # 选中的项如果没了，清掉选择
        if self._selected is not None and self._selected not in wanted:
            self._selected = None
            self.selection_changed.emit("")

        has_rows = bool(items) or bool(self._pending_removal)
        self._empty.setVisible(not has_rows)

    def _remove_row(self, screen_id: str) -> None:
        row = self._rows.pop(screen_id, None)
        if row is None:
            return
        self._pending_removal.add(screen_id)

        def finish() -> None:
            self._pending_removal.discard(screen_id)
            self._layout.removeWidget(row)
            row.setParent(None)
            row.deleteLater()
            self._empty.setVisible(not self._rows and not self._pending_removal)

        row.animate_out(finish)
