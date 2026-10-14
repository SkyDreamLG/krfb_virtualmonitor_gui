"""配色与样式表。跟随系统明暗，不硬编码单一主题。

颜色集中在这里，矢量绘制代码只引用语义名（success/warning/…），
这样换主题时不用改任何绘制逻辑。
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtGui import QColor, QFont, QPalette
from PySide6.QtWidgets import QApplication


@dataclass(frozen=True)
class Palette:
    dark: bool

    bg: str
    surface: str
    surface_alt: str
    surface_hover: str
    border: str
    border_strong: str

    text: str
    text_dim: str
    text_faint: str

    accent: str
    accent_dim: str
    success: str
    warning: str
    danger: str

    # --- 语义快捷方式 -------------------------------------------------------
    def color(self, name: str) -> QColor:
        return QColor(getattr(self, name))

    def alpha(self, name: str, a: float) -> QColor:
        return with_alpha(QColor(getattr(self, name)), a)


def with_alpha(color: QColor, alpha: float) -> QColor:
    """返回带指定透明度的颜色副本。自绘代码里到处都要用。"""
    result = QColor(color)
    result.setAlphaF(max(0.0, min(1.0, alpha)))
    return result


def font_at(base: QFont, delta: float, *, minimum: float = 7.5,
            bold: bool | None = None) -> QFont:
    """在基准字体上做相对缩放。

    不能直接写 `font.pointSizeF() + delta` —— 如果字体是用**像素**尺寸定义的，
    `pointSizeF()` 会返回 -1，结果就是负字号（Qt 会刷 "Point size <= 0" 警告
    并且字号完全失控）。这里先归一化到点值再计算。
    """
    result = QFont(base)
    size = result.pointSizeF()
    if size <= 0:
        pixels = result.pixelSize()
        # 96 DPI 下 1pt = 1.333px，即 px * 0.75
        size = pixels * 0.75 if pixels > 0 else 10.0
    result.setPointSizeF(max(minimum, size + delta))
    if bold is not None:
        result.setBold(bold)
    return result


LIGHT = Palette(
    dark=False,
    bg="#f4f5f7",
    surface="#ffffff",
    surface_alt="#eef0f3",
    surface_hover="#e7eaef",
    border="#d9dde3",
    border_strong="#c2c8d0",
    text="#191b1f",
    text_dim="#5f6672",
    text_faint="#9aa1ac",
    accent="#2f6fed",
    accent_dim="#c9dbfb",
    success="#12894a",
    warning="#b45309",
    danger="#c62828",
)

DARK = Palette(
    dark=True,
    bg="#16171b",
    surface="#1e2025",
    surface_alt="#26292f",
    surface_hover="#2e323a",
    border="#33373f",
    border_strong="#454a54",
    text="#e7e9ed",
    text_dim="#a2a8b3",
    text_faint="#6d7480",
    accent="#5b9bff",
    accent_dim="#2a3b57",
    success="#3ddc84",
    warning="#f5b13d",
    danger="#ff6b6b",
)


def detect_palette(app: QApplication | None = None) -> Palette:
    """按系统调色板的明度选择主题，而不是去猜桌面环境。"""
    app = app or QApplication.instance()
    if app is None:
        return DARK
    window = app.palette().color(QPalette.ColorRole.Window)
    # 亮度阈值 128 是 Qt 自身判断明暗的常用做法
    return DARK if window.lightness() < 128 else LIGHT


def qt_palette(p: Palette) -> QPalette:
    """把主题转成 QPalette。

    只靠 QSS 是不够的：`QMainWindow { background: ... }` 并不会可靠地传播到
    中央控件，结果是"文字用暗色主题、背景还是系统亮色"，对比度直接崩掉。
    铺一层真正的 QPalette 才能让窗口、菜单、工具提示这些默认绘制的部分
    都拿到正确的底色。
    """
    qp = QPalette()
    bg = QColor(p.bg)
    surface = QColor(p.surface)
    text = QColor(p.text)
    accent = QColor(p.accent)

    qp.setColor(QPalette.ColorRole.Window, bg)
    qp.setColor(QPalette.ColorRole.WindowText, text)
    qp.setColor(QPalette.ColorRole.Base, surface)
    qp.setColor(QPalette.ColorRole.AlternateBase, QColor(p.surface_alt))
    qp.setColor(QPalette.ColorRole.Text, text)
    qp.setColor(QPalette.ColorRole.Button, surface)
    qp.setColor(QPalette.ColorRole.ButtonText, text)
    qp.setColor(QPalette.ColorRole.BrightText, QColor(p.danger))
    qp.setColor(QPalette.ColorRole.Highlight, accent)
    qp.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    qp.setColor(QPalette.ColorRole.ToolTipBase, surface)
    qp.setColor(QPalette.ColorRole.ToolTipText, text)
    qp.setColor(QPalette.ColorRole.PlaceholderText, QColor(p.text_faint))
    qp.setColor(QPalette.ColorRole.Link, accent)

    disabled = QColor(p.text_faint)
    for role in (QPalette.ColorRole.WindowText, QPalette.ColorRole.Text,
                 QPalette.ColorRole.ButtonText):
        qp.setColor(QPalette.ColorGroup.Disabled, role, disabled)
    return qp


def stylesheet(p: Palette) -> str:
    """全局样式表。只做系统控件的基础统一，复杂的视觉都走自绘。"""
    return f"""
    QWidget {{
        color: {p.text};
        font-size: 13px;
    }}
    QMainWindow, QDialog, QWidget#central {{ background: {p.bg}; }}
    QSplitter, QStatusBar {{ background: {p.bg}; }}

    QLabel[role="title"] {{ font-size: 15px; font-weight: 600; }}
    QLabel[role="h1"]    {{ font-size: 19px; font-weight: 600; letter-spacing: 0.2px; }}
    QLabel[role="dim"]   {{ color: {p.text_dim}; }}
    QLabel[role="faint"] {{ color: {p.text_faint}; font-size: 12px; }}
    QLabel[role="mono"]  {{
        font-family: "JetBrains Mono", "Fira Code", "DejaVu Sans Mono", monospace;
        font-size: 12px;
    }}

    QPushButton {{
        background: {p.surface};
        border: 1px solid {p.border};
        border-radius: 7px;
        padding: 6px 14px;
        min-height: 18px;
    }}
    QPushButton:hover  {{ background: {p.surface_hover}; border-color: {p.border_strong}; }}
    QPushButton:pressed {{ background: {p.surface_alt}; }}
    QPushButton:disabled {{ color: {p.text_faint}; background: {p.surface_alt}; }}
    QPushButton[accent="true"] {{
        background: {p.accent};
        border-color: {p.accent};
        color: #ffffff;
        font-weight: 600;
    }}
    QPushButton[accent="true"]:hover {{ background: {p.accent}; border-color: {p.text}; }}
    QPushButton[accent="true"]:disabled {{
        background: {p.surface_alt}; border-color: {p.border}; color: {p.text_faint};
    }}
    QPushButton[danger="true"] {{ color: {p.danger}; }}
    QPushButton[danger="true"]:hover {{
        background: {p.danger}; border-color: {p.danger}; color: #ffffff;
    }}
    /* 纯图标按钮：清零内边距，否则 28px 的水平内边距会把固定宽高的小按钮
       里的图标挤扁 / 裁切。用 icons.mark_icon_only() 打上这个属性。 */
    QPushButton[iconOnly="true"] {{
        padding: 0;
        min-height: 0;
    }}

    QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QPlainTextEdit {{
        background: {p.surface};
        border: 1px solid {p.border};
        border-radius: 7px;
        padding: 5px 9px;
        selection-background-color: {p.accent};
        selection-color: #ffffff;
    }}
    QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus,
    QComboBox:focus, QPlainTextEdit:focus {{ border-color: {p.accent}; }}
    QLineEdit:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled, QComboBox:disabled {{
        background: {p.surface_alt}; color: {p.text_dim};
    }}
    QComboBox::drop-down {{ border: none; width: 20px; }}
    QComboBox QAbstractItemView {{
        background: {p.surface};
        border: 1px solid {p.border};
        selection-background-color: {p.accent};
        selection-color: #ffffff;
        outline: none;
    }}

    QCheckBox {{ spacing: 7px; }}
    QCheckBox::indicator {{
        width: 16px; height: 16px;
        border: 1px solid {p.border_strong};
        border-radius: 4px;
        background: {p.surface};
    }}
    QCheckBox::indicator:checked {{ background: {p.accent}; border-color: {p.accent}; }}

    QScrollArea {{ border: none; background: transparent; }}
    QScrollBar:vertical {{ background: transparent; width: 10px; margin: 2px; }}
    QScrollBar::handle:vertical {{
        background: {p.border_strong}; border-radius: 5px; min-height: 28px;
    }}
    QScrollBar::handle:vertical:hover {{ background: {p.text_faint}; }}
    QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; }}
    QScrollBar::add-page, QScrollBar::sub-page {{ background: transparent; }}
    QScrollBar:horizontal {{ background: transparent; height: 10px; margin: 2px; }}
    QScrollBar::handle:horizontal {{
        background: {p.border_strong}; border-radius: 5px; min-width: 28px;
    }}

    QToolTip {{
        background: {p.surface};
        color: {p.text};
        border: 1px solid {p.border};
        border-radius: 6px;
        padding: 5px 8px;
    }}

    QMenu {{
        background: {p.surface};
        border: 1px solid {p.border};
        border-radius: 8px;
        padding: 5px;
    }}
    QMenu::item {{ padding: 6px 22px 6px 12px; border-radius: 5px; }}
    QMenu::item:selected {{ background: {p.accent}; color: #ffffff; }}
    QMenu::separator {{ height: 1px; background: {p.border}; margin: 4px 8px; }}

    QStatusBar {{ color: {p.text_dim}; }}
    QStatusBar::item {{ border: none; }}

    QSplitter::handle {{ background: {p.border}; width: 1px; }}

    QGroupBox {{
        border: 1px solid {p.border};
        border-radius: 9px;
        margin-top: 10px;
        padding-top: 10px;
        font-weight: 600;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 11px;
        padding: 0 5px;
        color: {p.text_dim};
    }}
    """
