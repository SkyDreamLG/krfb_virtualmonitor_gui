"""内嵌 SVG 图标。

用字符串内嵌而不是资源文件：不依赖安装路径、不依赖 qrc 编译，还能按主题色
实时着色（同一个图标在明暗主题下各渲染一次即可）。
"""

from __future__ import annotations

from PySide6.QtCore import QByteArray, QRectF, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

# 线性图标（描边风格，Feather 风格 24x24 网格）
_STROKE_BODIES: dict[str, str] = {
    "plus": '<path d="M12 5v14M5 12h14"/>',
    "refresh": '<path d="M21 12a9 9 0 1 1-2.64-6.36"/><path d="M21 3v6h-6"/>',
    "edit": '<path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"/>',
    "trash": (
        '<path d="M3 6h18"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/>'
        '<path d="M10 11v6M14 11v6"/>'
        '<path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/>'
    ),
    "log": (
        '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>'
        '<path d="M14 2v6h6"/><path d="M8 13h8M8 17h8"/>'
    ),
    "scan": '<circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/>',
    "copy": (
        '<rect x="9" y="9" width="12" height="12" rx="2"/>'
        '<path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>'
    ),
    "eye": '<path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7-11-7-11-7z"/><circle cx="12" cy="12" r="3"/>',
    "eye-off": (
        '<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/>'
        '<path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/>'
        '<path d="M1 1l22 22"/>'
    ),
    "check": '<path d="M20 6L9 17l-5-5"/>',
    "warning": (
        '<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>'
        '<path d="M12 9v4"/><path d="M12 17h.01"/>'
    ),
    "monitor": (
        '<rect x="2" y="3" width="20" height="14" rx="2"/>'
        '<path d="M8 21h8M12 17v4"/>'
    ),
    "close": '<path d="M18 6L6 18M6 6l12 12"/>',
    "power": '<path d="M18.36 6.64a9 9 0 1 1-12.73 0"/><path d="M12 2v10"/>',
    "tune": (
        '<path d="M4 21v-7M4 10V3M12 21v-9M12 8V3M20 21v-5M20 12V3"/>'
        '<path d="M1 14h6M9 8h6M17 16h6"/>'
    ),
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "info": '<circle cx="12" cy="12" r="9"/><path d="M12 16v-5"/><path d="M12 8h.01"/>',
    "lock": (
        '<rect x="4" y="11" width="16" height="10" rx="2"/>'
        '<path d="M8 11V7a4 4 0 0 1 8 0v4"/>'
    ),
    "unlock": (
        '<rect x="4" y="11" width="16" height="10" rx="2"/>'
        '<path d="M8 11V7a4 4 0 0 1 7.5-2"/>'
    ),
    "tray": '<path d="M3 3h18v12H3z"/><path d="M3 9h18"/>',
}

# 需要填充而非描边的图标
_FILL_BODIES: dict[str, str] = {
    "play": '<path d="M7 4.5v15a1 1 0 0 0 1.52.85l12-7.5a1 1 0 0 0 0-1.7l-12-7.5A1 1 0 0 0 7 4.5z"/>',
    "stop": '<rect x="6" y="6" width="12" height="12" rx="1.5"/>',
    "dot": '<circle cx="12" cy="12" r="5"/>',
}

_STROKE_TEMPLATE = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
    'stroke="{color}" stroke-width="{weight}" stroke-linecap="round" '
    'stroke-linejoin="round" stroke-opacity="{opacity}">{body}</svg>'
)
_FILL_TEMPLATE = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
    'fill="{color}" fill-opacity="{opacity}">{body}</svg>'
)

_cache: dict[tuple[str, str, int, float], QPixmap] = {}

AVAILABLE = tuple(sorted({*_STROKE_BODIES, *_FILL_BODIES}))


def _svg_source(name: str, color: str, weight: float, opacity: float) -> str:
    """生成 SVG 源码。

    **颜色必须是 `#RRGGBB`，不能用 `#AARRGGBB`。** 实测 Qt 的 SVG 解析器不认
    8 位十六进制：填充色会被静默降级成黑色，描边色则直接什么都不画（图标消失）。
    透明度要单独用 stroke-opacity / fill-opacity 表达。
    """
    if name in _FILL_BODIES:
        return _FILL_TEMPLATE.format(color=color, opacity=opacity, body=_FILL_BODIES[name])
    body = _STROKE_BODIES.get(name)
    if body is None:
        # 开发者错误（图标名写错），面向代码而不是用户，不翻译
        raise KeyError(f"unknown icon {name!r}; available: {', '.join(AVAILABLE)}")
    return _STROKE_TEMPLATE.format(color=color, weight=weight, opacity=opacity, body=body)


def pixmap(name: str, color: QColor | str, size: int = 18, *, weight: float = 2.0,
           dpr: float = 0.0) -> QPixmap:
    """把图标渲染成指定颜色的位图（带缓存）。dpr=0 表示自动取屏幕缩放。"""
    qcolor = QColor(color) if not isinstance(color, QColor) else QColor(color)
    color_str = qcolor.name(QColor.NameFormat.HexRgb)
    opacity = round(qcolor.alphaF(), 3)

    if dpr <= 0:
        from PySide6.QtWidgets import QApplication

        app = QApplication.instance()
        dpr = app.devicePixelRatio() if app is not None else 1.0

    key = (name, f"{color_str}/{opacity}", size, dpr)
    cached = _cache.get(key)
    if cached is not None:
        return cached

    renderer = QSvgRenderer(
        QByteArray(_svg_source(name, color_str, weight, opacity).encode())
    )
    pixel_size = max(1, int(round(size * dpr)))
    pix = QPixmap(pixel_size, pixel_size)
    pix.setDevicePixelRatio(dpr)
    pix.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    # 关键：setDevicePixelRatio 之后，QPainter 的坐标系**已经**按 DPR 缩放过了，
    # 所以这里必须用逻辑尺寸 size 绘制。之前误用了 pixel_size（设备像素），
    # 等于画布放大 dpr 倍、内容再放大 dpr 倍 —— dpr=1.25 时图标就会被放大 1.25 倍
    # 并裁掉右/下边缘（「+」被裁成「—」，图标全部残缺）。dpr=1 时恰好看不出来。
    #
    # 这个 inset 决定 24 单位的 viewBox 映射到哪里，也就是图标四周留多少边距。
    # 不能太小：eye / tune / eye-off 这些图标的路径本身横跨 viewBox 的 1..23，
    # 而 stroke-width=2 的描边以路径为中心向外扩 1 个单位，正好占满 0..24。
    # 边距小于 1 像素时描边两端会被切平。8% 在 18px 下约 1.4px，足够。
    inset = size * 0.08
    renderer.render(painter, QRectF(inset, inset, size - 2 * inset, size - 2 * inset))
    painter.end()

    _cache[key] = pix
    return pix


def icon(name: str, color: QColor | str, size: int = 18, *, weight: float = 2.0) -> QIcon:
    return QIcon(pixmap(name, color, size, weight=weight))


def mark_icon_only(button) -> None:
    """把按钮标记成"纯图标"，让样式表把内边距清零。

    全局 QPushButton 规则带 `padding: 6px 14px`，也就是水平方向要占 28px。
    固定宽高的小按钮（24~38px）放不下「图标 + 28px 内边距」，
    结果就是图标被挤扁或裁切 —— 必须有这个标记，否则图标按钮永远显示不完整。
    """
    button.setProperty("iconOnly", True)


def app_icon(color: QColor | str = "#2f6fed", size: int = 256) -> QIcon:
    """程序图标：显示器外框 + 内部信号弧。"""
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
        f'stroke="{QColor(color).name()}" stroke-width="1.8" stroke-linecap="round" '
        'stroke-linejoin="round">'
        '<rect x="2" y="3.5" width="20" height="13" rx="2.2"/>'
        '<path d="M8 20.5h8"/><path d="M12 16.5v4"/>'
        '<path d="M8.6 12.8a4.6 4.6 0 0 1 6.8 0"/>'
        '<path d="M10.4 10.4a7 7 0 0 1 3.2 0"/>'
        "</svg>"
    )
    renderer = QSvgRenderer(QByteArray(svg.encode()))
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    renderer.render(painter)
    painter.end()
    return QIcon(pix)
