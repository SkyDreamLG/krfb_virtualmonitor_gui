"""实时日志查看窗口。

用轮询文件增量而不是 QFileSystemWatcher —— krfb 的输出是持续追加的，
watcher 在追加场景下容易丢事件；按字节偏移增量读取简单且不会重复。

内存有上限：`setMaximumBlockCount` 保证长时间运行也不会把内存吃光。
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QTextCharFormat, QTextCursor
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..i18n import tr, trf
from . import icons
from .theme import Palette
from .vector import StatusDot

MAX_BLOCKS = 4000  # ~ 足够覆盖一次会话，又不会无限增长
POLL_MS = 500


def _empty_log() -> str:
    """空日志占位文案。函数而不是常量 —— 绝不在 import 期调用 tr()。"""
    return tr("(No output yet)\n\nThis is empty until the virtual screen is started.")


class LogViewer(QDialog):
    """按屏幕 id 打开的日志窗口。"""

    def __init__(self, palette: Palette, screen_name: str, log_path: Path,
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._palette = palette
        self._path = log_path
        self._screen_name = screen_name
        self._offset = 0
        self._raw = ""

        self.setWindowTitle(f"{tr('Log')} · {screen_name}")
        self.resize(760, 460)
        self.setModal(False)

        # --- 顶部：搜索 + 选项 ---
        self._search = QLineEdit()
        self._search.setPlaceholderText(tr("Search… (press Enter for the next match)"))
        self._search.setClearButtonEnabled(True)

        self._auto_scroll = QCheckBox(tr("Auto-scroll"))
        self._auto_scroll.setChecked(True)

        self._reload = QPushButton(tr("Reload"))
        self._reload.setIcon(icons.icon("refresh", palette.color("text"), 14))
        self._open_dir = QPushButton(tr("Open containing folder"))

        # 实时指示点
        self._live_dot = _LiveDot(palette)

        head = QHBoxLayout()
        head.setSpacing(8)
        head.addWidget(self._search, 1)
        head.addWidget(self._auto_scroll)
        head.addWidget(self._live_dot)
        head.addWidget(self._reload)
        head.addWidget(self._open_dir)

        # --- 正文 ---
        self._text = QPlainTextEdit()
        self._text.setReadOnly(True)
        self._text.setMaximumBlockCount(MAX_BLOCKS)
        mono = QFont("JetBrains Mono")
        mono.setStyleHint(QFont.StyleHint.Monospace)
        mono.setFamilies(["JetBrains Mono", "Fira Code", "DejaVu Sans Mono", "monospace"])
        mono.setPointSizeF(9.5)
        self._text.setFont(mono)
        self._text.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self._text.setStyleSheet(
            f"QPlainTextEdit{{background:{palette.color('surface_alt').name()};"
            f"border:1px solid {palette.color('border').name()};"
            f"border-radius:8px; padding:8px;}}"
        )

        # --- 底部状态行 ---
        self._status = QLabel()
        self._status.setProperty("role", "faint")

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(9)
        root.addLayout(head)
        root.addWidget(self._text, 1)
        root.addWidget(self._status)

        self._search.returnPressed.connect(self._find_next)
        self._reload.clicked.connect(self._full_reload)
        self._open_dir.clicked.connect(self._open_directory)

        self._timer = QTimer(self)
        self._timer.setInterval(POLL_MS)
        self._timer.timeout.connect(self._poll)
        self._timer.start()

        self._full_reload()

    # --- 读取 ---------------------------------------------------------------
    def _read_new(self) -> str:
        try:
            size = self._path.stat().st_size
        except OSError:
            return ""
        if size < self._offset:
            # 文件被截断（重新启动虚拟屏时会发生），从头再读
            self._offset = 0
        if size == self._offset:
            return ""
        try:
            with open(self._path, "rb") as handle:
                handle.seek(self._offset)
                data = handle.read()
                self._offset = size
        except OSError:
            return ""
        return data.decode("utf-8", "replace")

    def _poll(self) -> None:
        chunk = self._read_new()
        if not chunk:
            return
        self._raw += chunk
        self._append(chunk)

    def _append(self, chunk: str) -> None:
        at_bottom = self._auto_scroll.isChecked()
        cursor = self._text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        if at_bottom:
            self._text.setTextCursor(cursor)
        self._text.insertPlainText(chunk)
        if at_bottom:
            bar = self._text.verticalScrollBar()
            bar.setValue(bar.maximum())
        self._update_status()

    def _full_reload(self) -> None:
        self._offset = 0
        self._raw = ""
        self._text.clear()
        chunk = self._read_new()
        if chunk:
            self._raw = chunk
            self._text.setPlainText(chunk)
            bar = self._text.verticalScrollBar()
            bar.setValue(bar.maximum())
        self._update_status()
        if not self._raw:
            self._text.setPlainText(_empty_log())

    def _update_status(self) -> None:
        lines = self._raw.count("\n") + 1 if self._raw else 0
        try:
            size = self._path.stat().st_size
        except OSError:
            size = 0
        self._status.setText(trf("{path}   ·   {lines} lines   ·   {size} bytes",
                                 path=self._path, lines=lines, size=size))

    # --- 操作 ---------------------------------------------------------------
    def _find_next(self) -> None:
        needle = self._search.text()
        if not needle:
            return
        if not self._text.find(needle):
            # 到底了就从开头再来一遍
            cursor = self._text.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            self._text.setTextCursor(cursor)
            if not self._text.find(needle):
                self._status.setText(trf("No match for \"{needle}\"", needle=needle))
                return
        self._highlight_current()

    def retranslate(self) -> None:
        """语言切换后重设文案。刻意不调 _full_reload()：那会把读取偏移清零、
        整份日志重读一遍。"""
        self.setWindowTitle(f"{tr('Log')} · {self._screen_name}")
        self._search.setPlaceholderText(tr("Search… (press Enter for the next match)"))
        self._auto_scroll.setText(tr("Auto-scroll"))
        self._reload.setText(tr("Reload"))
        self._open_dir.setText(tr("Open containing folder"))
        self._live_dot.retranslate()
        if not self._raw:
            self._text.setPlainText(_empty_log())
        self._update_status()

    def _highlight_current(self) -> None:
        cursor = self._text.textCursor()
        selection = QTextCharFormat()
        selection.setBackground(self._palette.color("accent"))
        selection.setForeground(self._palette.color("surface"))
        cursor.mergeCharFormat(selection)

    def _open_directory(self) -> None:
        from PySide6.QtCore import QUrl
        from PySide6.QtGui import QDesktopServices

        QDesktopServices.openUrl(QUrl.fromLocalFile(str(self._path.parent)))

    def closeEvent(self, event) -> None:  # noqa: N802
        self._timer.stop()
        super().closeEvent(event)


class _LiveDot(StatusDot):
    """日志窗口右上角的"实时"指示点，复用状态点的脉冲动画。"""

    def __init__(self, palette: Palette, parent: QWidget | None = None) -> None:
        from .vector import Clock

        self._own_clock = Clock(period_ms=1700)
        super().__init__(self._own_clock, palette, diameter=18, parent=parent)
        self.set_state(palette.color("success"), True)
        self.retranslate()

    def retranslate(self) -> None:
        # 秒数从 POLL_MS 推出来，改轮询间隔时提示不会说谎
        self.setToolTip(trf("Refreshes every {seconds} s", seconds=POLL_MS / 1000))
