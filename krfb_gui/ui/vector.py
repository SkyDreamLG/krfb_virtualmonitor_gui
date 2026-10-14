"""矢量动画组件。全部用 QPainter 绘制，不依赖任何位图资源。

几个已实测确认、必须遵守的约束：

1. **路径裁剪不能直接用 pointAtPercent 切。** Qt 把百分比映射到贝塞尔的 t 参数，
   而不是弧长。同一段 cubic，pointAtPercent(0.25) 得到 (13.78, 20.75)，而真正
   25% 弧长处是 (11.82, 19.43)。必须走 `length() → percentAtLength() →
   pointAtPercent()`，并且**在弧长空间均匀采样**才得到视觉上匀速的描边。

2. **QGraphicsOpacityEffect 不能挂在顶层窗口上。** 实测：无 effect 渲染得到
   0xffff0000，顶层挂 0.5 的 effect 得到全透明 0x00000000（整个窗口不渲染）。
   所以淡入淡出要么作用于子控件，要么像主窗口的 NoticeBar 那样在 paintEvent
   里直接乘 alpha。

3. **一个列表共用一个时钟，而不是每行一个动画。** 否则 20 个屏幕就是 20 个定时器
   和每帧 20 次重绘。窗口隐藏时统一暂停。
"""

from __future__ import annotations

from PySide6.QtCore import (
    Property,
    QEasingCurve,
    QObject,
    QPointF,
    QPropertyAnimation,
    QRectF,
    Qt,
    QVariantAnimation,
    Signal,
)
from PySide6.QtGui import (
    QColor,
    QFontMetrics,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
)
from PySide6.QtWidgets import QWidget

from .theme import Palette, font_at, with_alpha

# 缓动曲线要实例化后才能求值 —— `QEasingCurve.Type.X.valueForProgress` 在
# PySide6 里不存在，必须 QEasingCurve(QEasingCurve.Type.X).valueForProgress(t)
_INOUT_SINE = QEasingCurve(QEasingCurve.Type.InOutSine)


def ease_in_out_sine(t: float) -> float:
    return _INOUT_SINE.valueForProgress(t)


def trimmed_path(path: QPainterPath, fraction: float, samples: int = 72) -> QPainterPath:
    """把路径裁到前 `fraction` 比例（按**弧长**，不是贝塞尔参数）。

    用于"一笔画出来"的描边动画。在弧长空间均匀采样再连成折线，
    采样足够密时视觉上完全平滑。
    """
    total = path.length()
    if total <= 0.0 or fraction <= 0.0:
        return QPainterPath()
    if fraction >= 1.0:
        return QPainterPath(path)

    clamped = min(fraction, 1.0)
    target = total * clamped
    count = max(2, int(samples * clamped) + 2)

    result = QPainterPath()
    for index in range(count + 1):
        length = target * index / count
        point = path.pointAtPercent(path.percentAtLength(length))
        if index == 0:
            result.moveTo(point)
        else:
            result.lineTo(point)
    return result


class Clock(QObject):
    """整个界面共用的动画时钟。

    一条 QVariantAnimation 驱动所有脉冲元素。起止值必须是 **float** ——
    整数会得到台阶式的跳变。中点设峰值是为了做出"呼吸"而不是锯齿。
    """

    tick = Signal(float)  # 相位 0..1

    def __init__(self, period_ms: int = 1900, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._anim = QVariantAnimation(self)
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.setDuration(period_ms)
        self._anim.setLoopCount(-1)
        self._anim.setKeyValueAt(0.5, 1.0)
        self._anim.valueChanged.connect(self._emit)
        self._running = False

    def _emit(self, value: object) -> None:
        self.tick.emit(float(value))  # PySide6 传过来是 object

    def start(self) -> None:
        if not self._running:
            self._running = True
            self._anim.start()

    def pause(self) -> None:
        if self._running:
            self._running = False
            self._anim.pause()

    def set_active(self, active: bool) -> None:
        """窗口隐藏时暂停，避免缩在托盘里还满帧重绘。"""
        self.start() if active else self.pause()


class StatusDot(QWidget):
    """状态指示点 + 运行时的脉冲环。

    只在 running 状态下才接入时钟；停止状态的实例完全不参与重绘。
    """

    def __init__(self, clock: Clock, palette: Palette, diameter: int = 26,
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._clock = clock
        self._palette = palette
        self._diameter = diameter
        self._color = palette.color("text_faint")
        self._running = False
        self._phase = 0.0
        self._grow = 0.0
        self.setFixedSize(diameter, diameter)

        self._morph = QVariantAnimation(self)
        self._morph.setDuration(280)
        self._morph.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._morph.valueChanged.connect(self._on_morph)

    def set_state(self, color: QColor, running: bool) -> None:
        if color.name() != self._color.name():
            self._color = QColor(color)
            self.update()

        if running and not self._running:
            self._running = True
            self._clock.tick.connect(self._on_tick)
            self._clock.start()
            self._morph.stop()
            self._morph.setStartValue(0.0)
            self._morph.setEndValue(1.0)
            self._morph.start()
        elif not running and self._running:
            self._running = False
            try:
                self._clock.tick.disconnect(self._on_tick)
            except (RuntimeError, TypeError):
                pass
            self._phase = 0.0
            self._grow = 0.0
            self.update()

    def _on_tick(self, phase: float) -> None:
        self._phase = phase
        self.update()

    def _on_morph(self, value: object) -> None:
        self._grow = float(value)
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802 - Qt 命名约定
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        center = QPointF(self.width() / 2, self.height() / 2)
        base_radius = self._diameter * 0.25

        if self._running:
            # 两圈错开半个相位的扩散环
            pen = QPen()
            pen.setWidthF(1.6)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            for offset in (0.0, 0.5):
                ring = (self._phase + offset) % 1.0
                radius = base_radius + ring * (self._diameter * 0.38)
                pen.setColor(with_alpha(self._color, ((1.0 - ring) ** 1.8) * 0.45))
                painter.setPen(pen)
                painter.drawEllipse(center, radius, radius)

        # 实心点：启动瞬间从 0 放大到 1
        grow = self._grow if self._running else 1.0
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._color)
        painter.drawEllipse(center, base_radius * (0.35 + 0.65 * grow), base_radius * (0.35 + 0.65 * grow))


class LogoMark(QWidget):
    """标题栏 logo：显示器轮廓 + 沿信号弧巡游的光点。"""

    def __init__(self, clock: Clock, palette: Palette, size: int = 30,
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._clock = clock
        self._palette = palette
        self._phase = 0.0
        self.setFixedSize(size, size)
        clock.tick.connect(self._on_tick)
        clock.start()

        # 光点巡游的基准弧（归一化坐标）
        self._travel = QPainterPath()
        self._travel.moveTo(0.28, 0.70)
        self._travel.quadTo(0.50, 0.24, 0.72, 0.70)

    def _on_tick(self, phase: float) -> None:
        self._phase = phase
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        side = min(self.width(), self.height())
        painter.translate((self.width() - side) / 2, (self.height() - side) / 2)
        painter.scale(side, side)  # 之后全部用 0..1 归一化坐标

        accent = self._palette.color("accent")
        dim = with_alpha(accent, 0.28)

        # 显示器外框 + 底座
        pen = QPen(dim)
        pen.setWidthF(0.052)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(QRectF(0.08, 0.13, 0.84, 0.54), 0.09, 0.09)
        painter.drawLine(QPointF(0.38, 0.85), QPointF(0.62, 0.85))
        painter.drawLine(QPointF(0.50, 0.67), QPointF(0.50, 0.85))

        # 三段信号弧，越靠内越亮
        for index, scale in enumerate((1.0, 0.70, 0.42)):
            alpha = 0.20 + 0.15 * index
            ring = QPen(with_alpha(accent, alpha))
            ring.setWidthF(0.048)
            ring.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(ring)
            radius_x, radius_y = 0.30 * scale, 0.30 * scale
            arc = QPainterPath()
            arc.moveTo(0.50 - radius_x, 0.70)
            arc.quadTo(0.50, 0.70 - radius_y * 1.8, 0.50 + radius_x, 0.70)
            painter.drawPath(arc)

        # 巡游光点：phase 驱动，来回往返而不是瞬移回起点
        travel = self._phase * 2.0
        if travel > 1.0:
            travel = 2.0 - travel
        eased = ease_in_out_sine(travel)
        point = self._travel.pointAtPercent(eased)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(with_alpha(accent, 0.26))
        painter.drawEllipse(point, 0.088, 0.088)
        painter.setBrush(accent)
        painter.drawEllipse(point, 0.046, 0.046)


class AspectPreview(QWidget):
    """分辨率矢量预览：切换分辨率时，矩形从旧宽高比**平滑形变**到新宽高比。

    用 QPropertyAnimation 驱动一个 float 属性，比逐帧重算几何干净得多。
    """

    def __init__(self, palette: Palette, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._palette = palette
        self._from_aspect = 16 / 9
        self._to_aspect = 16 / 9
        self._t = 1.0
        self._label = ""
        self._sublabel = ""
        self._warn = False
        self.setMinimumHeight(130)

        self._anim = QPropertyAnimation(self, b"progress", self)
        self._anim.setDuration(430)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    # --- 动画属性 -----------------------------------------------------------
    def _get_progress(self) -> float:
        return self._t

    def _set_progress(self, value: float) -> None:
        self._t = float(value)
        self.update()

    progress = Property(float, _get_progress, _set_progress)

    # --- 对外接口 -----------------------------------------------------------
    def current_aspect(self) -> float:
        return self._from_aspect + (self._to_aspect - self._from_aspect) * self._t

    def set_resolution(self, width: int, height: int, label: str = "", sublabel: str = "") -> None:
        aspect = width / height if height else 16 / 9
        self._label = label or f"{width}×{height}"
        self._sublabel = sublabel
        if abs(aspect - self._to_aspect) < 1e-4:
            self.update()
            return
        # 从中断处当前的宽高比出发，动画被打断也能平滑衔接
        self._from_aspect = self.current_aspect()
        self._to_aspect = aspect
        self._anim.stop()
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.start()

    def set_warning(self, warn: bool) -> None:
        if warn != self._warn:
            self._warn = warn
            self.update()

    # --- 绘制 ---------------------------------------------------------------
    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        pad = 14.0
        avail = QRectF(pad, pad, self.width() - 2 * pad, self.height() - 2 * pad)
        if avail.width() <= 8 or avail.height() <= 8:
            return

        aspect = max(0.15, min(6.0, self.current_aspect()))
        box_w = avail.width()
        box_h = box_w / aspect
        if box_h > avail.height():
            box_h = avail.height()
            box_w = box_h * aspect
        box = QRectF(
            avail.x() + (avail.width() - box_w) / 2,
            avail.y() + (avail.height() - box_h) / 2,
            box_w,
            box_h,
        )

        accent = self._palette.color("warning" if self._warn else "accent")

        gradient = QLinearGradient(box.topLeft(), box.bottomLeft())
        gradient.setColorAt(0.0, with_alpha(accent, 0.15))
        gradient.setColorAt(1.0, with_alpha(accent, 0.04))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(gradient)
        painter.drawRoundedRect(box, 7, 7)

        border = QPen(with_alpha(accent, 0.80))
        border.setWidthF(1.5)
        painter.setPen(border)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(box, 7, 7)

        # 三分栅格
        grid = QPen(with_alpha(accent, 0.18))
        grid.setWidthF(1.0)
        painter.setPen(grid)
        for fraction in (1 / 3, 2 / 3):
            x = box.left() + box.width() * fraction
            y = box.top() + box.height() * fraction
            painter.drawLine(QPointF(x, box.top() + 3), QPointF(x, box.bottom() - 3))
            painter.drawLine(QPointF(box.left() + 3, y), QPointF(box.right() - 3, y))

        if not self._label:
            return

        label_size = max(8.5, min(11.5, box.height() / 7.5))
        base_size = font_at(self.font(), 0.0, minimum=label_size).pointSizeF()
        font = font_at(self.font(), label_size - base_size, bold=True)
        metrics = QFontMetrics(font)
        main_rect = metrics.boundingRect(self._label)

        sub_font = font_at(font, -2.0)
        sub_metrics = QFontMetrics(sub_font)
        sub_rect = sub_metrics.boundingRect(self._sublabel) if self._sublabel else None

        block = main_rect.height() + (sub_metrics.height() + 3 if sub_rect else 0)
        top = box.center().y() - block / 2

        painter.setFont(font)
        painter.setPen(self._palette.color("text"))
        painter.drawText(
            QPointF(box.center().x() - main_rect.width() / 2, top + main_rect.height() - metrics.descent()),
            self._label,
        )

        if sub_rect is not None:
            painter.setFont(sub_font)
            painter.setPen(accent if self._warn else self._palette.color("text_dim"))
            painter.drawText(
                QPointF(box.center().x() - sub_rect.width() / 2,
                        top + main_rect.height() + sub_metrics.height() - sub_metrics.descent() + 3),
                self._sublabel,
            )


class DrawIcon(QWidget):
    """会"画出来"的图标（勾/叉/感叹号），用于端口可用性等即时反馈。"""

    def __init__(self, palette: Palette, kind: str = "check", size: int = 20,
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._palette = palette
        self._kind = kind
        self._color = palette.color("success")
        self._progress = 0.0
        # 区分"从未显示过"和"已显示为当前状态" —— 否则第一次调用会被去重逻辑吃掉
        self._shown = False
        self.setFixedSize(size, size)

        self._anim = QPropertyAnimation(self, b"progress", self)
        self._anim.setDuration(340)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def _get_progress(self) -> float:
        return self._progress

    def _set_progress(self, value: float) -> None:
        self._progress = float(value)
        self.update()

    progress = Property(float, _get_progress, _set_progress)

    def show_state(self, kind: str, color: QColor) -> None:
        """设置状态并播放"画出来"的动画。

        幂等：状态没变就什么都不做。这一点很关键 —— 调用方（比如对话框的
        实时校验）会在每次输入变化时调用本方法，如果每次重启动画，
        用户每敲一个字符图标就会闪回空白重新画，永远看不到完成态。
        """
        new_color = QColor(color)
        if self._shown and kind == self._kind and new_color.name() == self._color.name():
            return
        self._shown = True
        self._kind = kind
        self._color = new_color
        self._anim.stop()
        self._progress = 0.0
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.start()

    def clear(self) -> None:
        self._anim.stop()
        self._progress = 0.0
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        if self._progress <= 0.0:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        side = float(min(self.width(), self.height()))
        painter.translate((self.width() - side) / 2, (self.height() - side) / 2)
        painter.scale(side, side)

        pen = QPen(self._color)
        pen.setWidthF(0.115)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        path = QPainterPath()
        if self._kind == "check":
            path.moveTo(0.22, 0.52)
            path.lineTo(0.42, 0.71)
            path.lineTo(0.78, 0.30)
        elif self._kind == "cross":
            path.moveTo(0.28, 0.28)
            path.lineTo(0.72, 0.72)
            path.moveTo(0.72, 0.28)
            path.lineTo(0.28, 0.72)
        else:  # alert
            path.moveTo(0.50, 0.24)
            path.lineTo(0.50, 0.58)
            path.moveTo(0.50, 0.75)
            path.lineTo(0.50, 0.78)

        painter.drawPath(trimmed_path(path, self._progress, samples=40))


class Spinner(QWidget):
    """不定长进度指示：一段绕圆心旋转的弧，用于"启动中"。"""

    def __init__(self, palette: Palette, size: int = 18, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._palette = palette
        self._phase = 0.0
        self._color = palette.color("accent")
        self.setFixedSize(size, size)

        self._anim = QVariantAnimation(self)
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.setDuration(1100)
        self._anim.setLoopCount(-1)
        self._anim.valueChanged.connect(self._on_value)

    def set_color(self, color: QColor) -> None:
        self._color = QColor(color)
        self.update()

    def _on_value(self, value: object) -> None:
        self._phase = float(value)
        self.update()

    def start(self) -> None:
        self._anim.start()

    def stop(self) -> None:
        self._anim.stop()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        side = min(self.width(), self.height())
        margin = 2.0
        rect = QRectF(margin, margin, side - 2 * margin, side - 2 * margin)

        track = QPen(with_alpha(self._color, 0.22))
        track.setWidthF(2.0)
        painter.setPen(track)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(rect)

        arc = QPen(self._color)
        arc.setWidthF(2.0)
        arc.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(arc)
        # Qt 的角度单位是 1/16 度；负的 span 表示顺时针
        start = int(-self._phase * 360 * 16)
        painter.drawArc(rect, start, 100 * 16)

