"""辅助对话框：密码补录、外部进程认领、设置与关于。"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from .. import autostart, constants as C
from .. import i18n, prefs
from ..i18n import tr, trf
from ..models import ProcInfo
from ..secrets import SecretsStatus, compose_detail, generate_password
from . import icons
from .theme import Palette


class PasswordPrompt(QDialog):
    """当密钥环不可用时，向用户补录密码。"""

    def __init__(self, palette: Palette, screen_name: str, reason: str,
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._palette = palette
        self.setWindowTitle(f"{tr('Password required')} · {screen_name}")
        self.setMinimumWidth(430)

        info = QLabel(reason)
        info.setWordWrap(True)
        info.setStyleSheet(
            f"color:{palette.color('warning').name()};"
            f"background:{palette.color('surface_alt').name()};"
            f"border-radius:7px; padding:9px 11px;"
        )

        self._password = QLineEdit()
        self._password.setEchoMode(QLineEdit.EchoMode.Password)
        self._password.setPlaceholderText(tr("Enter the VNC password for this virtual screen"))

        generate = QPushButton(tr("Random"))
        generate.clicked.connect(lambda: self._password.setText(generate_password()))

        row = QHBoxLayout()
        row.addWidget(self._password, 1)
        row.addWidget(generate)

        # 这是安全披露（明文经 ps 可见），不是教程文字，保留
        hint = QLabel(tr(
            "The password is passed to the krfb process in plain text, so other "
            "local users can see it via ps; VNC authentication only uses the "
            "first 8 characters."
        ))
        hint.setProperty("role", "faint")
        hint.setWordWrap(True)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText(tr("Use"))
        buttons.button(QDialogButtonBox.StandardButton.Ok).setProperty("accent", True)
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText(tr("Cancel"))
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self._password.textChanged.connect(
            lambda text: buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(bool(text))
        )
        buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 16, 18, 14)
        root.setSpacing(11)
        root.addWidget(info)
        root.addLayout(row)
        root.addWidget(hint)
        root.addWidget(buttons)

    @property
    def password(self) -> str:
        return self._password.text()


class AdoptDialog(QDialog):
    """认领外部启动的 krfb 进程。"""

    def __init__(self, palette: Palette, processes: list[ProcInfo],
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._palette = palette
        self.setWindowTitle(tr("Unmanaged virtual screens found"))
        self.setMinimumWidth(520)
        self._boxes: list[tuple[QCheckBox, ProcInfo]] = []

        intro = QLabel(tr(
            "These krfb-virtualmonitor processes were not started by this app. "
            "Import them to manage them here."
        ))
        intro.setWordWrap(True)
        intro.setProperty("role", "dim")

        holder = QWidget()
        holder_layout = QVBoxLayout(holder)
        holder_layout.setContentsMargins(2, 2, 2, 2)
        holder_layout.setSpacing(7)

        for info in processes:
            box = QCheckBox()
            box.setChecked(True)

            label = QLabel(
                trf("<b>{name}</b> · {resolution} · Port {port}<br>"
                    "<span style='font-size:11px'>PID {pid}</span>",
                    name=info.name,
                    resolution=info.resolution or tr("unknown resolution"),
                    port=info.port, pid=info.pid)
                + (tr("<br><span style='font-size:11px'>⚠ The package was upgraded; "
                      "restarting this virtual screen is recommended</span>")
                   if info.exe_is_deleted else "")
            )
            label.setTextFormat(Qt.TextFormat.RichText)
            label.setWordWrap(True)

            row = QHBoxLayout()
            row.setContentsMargins(0, 0, 0, 0)
            row.addWidget(box, 0, Qt.AlignmentFlag.AlignTop)
            row.addWidget(label, 1)

            container = QWidget()
            container.setLayout(row)
            container.setStyleSheet(
                f"background:{palette.color('surface_alt').name()}; border-radius:7px;"
            )
            holder_layout.addWidget(container)
            self._boxes.append((box, info))

        holder_layout.addStretch(1)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(holder)
        scroll.setMinimumHeight(180)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText(tr("Import selected"))
        buttons.button(QDialogButtonBox.StandardButton.Ok).setProperty("accent", True)
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText(tr("Cancel"))
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 16, 18, 14)
        root.setSpacing(11)
        root.addWidget(intro)
        root.addWidget(scroll, 1)
        root.addWidget(buttons)

    @property
    def selected(self) -> list[ProcInfo]:
        return [info for box, info in self._boxes if box.isChecked()]


class SettingsDialog(QDialog):
    """设置：语言、自启、密钥环状态、环境问题、关于。

    语言在这里可以即时切换：换了就 `i18n.set_preference()` + 自己
    `retranslate()`（用户正看着这个对话框）；主窗口在 `exec()` 返回后
    统一刷新（见 `MainWindow._on_settings`）。

    环境问题从 provider 现取而不是构造时快照 —— 切换语言后要能整段重算。
    """

    unlock_requested = None  # 由主窗口赋值（信号）

    def __init__(self, palette: Palette, warnings_provider, secrets_status: SecretsStatus,
                 secrets_raw_detail: str, krfb_version_source: str,
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._palette = palette
        self._warnings_provider = warnings_provider
        self._secrets_status = secrets_status
        self._secrets_raw_detail = secrets_raw_detail
        self._krfb_version_source = krfb_version_source
        self.setMinimumWidth(540)

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 16, 18, 14)
        root.setSpacing(13)

        # --- 语言 ---
        self._lang_box = QGroupBox()
        lang_layout = QVBoxLayout(self._lang_box)
        lang_row = QHBoxLayout()
        self._lang_combo = QComboBox()
        for pref in i18n.available_preferences():
            self._lang_combo.addItem(i18n.language_name(pref), pref)
        self._lang_combo.setCurrentIndex(
            max(0, self._lang_combo.findData(i18n.preference()))
        )
        lang_row.addWidget(self._lang_combo, 0)
        lang_row.addStretch(1)
        lang_layout.addLayout(lang_row)
        self._lang_error = QLabel()
        self._lang_error.setProperty("role", "faint")
        self._lang_error.setWordWrap(True)
        self._lang_error.hide()
        lang_layout.addWidget(self._lang_error)
        root.addWidget(self._lang_box)

        # --- 关闭窗口时的行为 ---
        self._close_box = QGroupBox()
        close_layout = QVBoxLayout(self._close_box)
        close_row = QHBoxLayout()
        self._close_combo = QComboBox()
        for action in prefs.CLOSE_ACTIONS:
            self._close_combo.addItem("", action)  # 文案在 retranslate 里设
        self._close_combo.setCurrentIndex(
            max(0, self._close_combo.findData(prefs.close_action()))
        )
        close_row.addWidget(self._close_combo, 0)
        close_row.addStretch(1)
        close_layout.addLayout(close_row)
        self._close_error = QLabel()
        self._close_error.setProperty("role", "faint")
        self._close_error.setWordWrap(True)
        self._close_error.hide()
        close_layout.addWidget(self._close_error)
        root.addWidget(self._close_box)

        # --- 开机自启 ---
        self._auto_box = QGroupBox()
        auto_layout = QVBoxLayout(self._auto_box)
        self._autostart = QCheckBox()
        self._autostart.setChecked(autostart.is_enabled())
        auto_layout.addWidget(self._autostart)

        self._autostart_error = QLabel()
        self._autostart_error.setProperty("role", "faint")
        self._autostart_error.setWordWrap(True)
        self._autostart_error.hide()
        auto_layout.addWidget(self._autostart_error)
        root.addWidget(self._auto_box)

        # --- 密钥环 ---
        self._key_box = QGroupBox()
        key_layout = QVBoxLayout(self._key_box)

        status_row = QHBoxLayout()
        tone = "success" if secrets_status is SecretsStatus.OK else "warning"
        self._key_status = QLabel()
        self._key_status.setStyleSheet(f"color:{palette.color(tone).name()}; font-weight:600;")
        status_row.addWidget(self._key_status)
        status_row.addStretch(1)
        self._unlock = QPushButton()
        self._unlock.setIcon(icons.icon("unlock", palette.color("text"), 14))
        self._unlock.setEnabled(secrets_status is SecretsStatus.LOCKED)
        status_row.addWidget(self._unlock)
        key_layout.addLayout(status_row)

        self._key_detail = QLabel()
        self._key_detail.setProperty("role", "faint")
        self._key_detail.setWordWrap(True)
        key_layout.addWidget(self._key_detail)
        root.addWidget(self._key_box)

        # --- 环境检查 ---
        self._env_box = QGroupBox()
        self._env_layout = QVBoxLayout(self._env_box)
        root.addWidget(self._env_box)

        # --- 关于 ---
        self._about_box = QGroupBox()
        about_layout = QVBoxLayout(self._about_box)
        self._about = QLabel()
        self._about.setTextFormat(Qt.TextFormat.RichText)
        self._about.setWordWrap(True)
        self._about.setProperty("role", "faint")
        about_layout.addWidget(self._about)
        root.addWidget(self._about_box)

        # 组都放进滚动区：屏幕矮或显示缩放高（1080p @200% 只有 540 逻辑像素）时
        # 至少保证底部的关闭按钮够得着
        self._groups = QWidget()
        groups_layout = QVBoxLayout(self._groups)
        groups_layout.setContentsMargins(0, 0, 0, 0)
        groups_layout.setSpacing(13)
        for box in (self._lang_box, self._close_box, self._auto_box, self._key_box,
                    self._env_box, self._about_box):
            groups_layout.addWidget(box)
        groups_layout.addStretch(1)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidget(self._groups)

        self._buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        self._buttons.rejected.connect(self.reject)
        self._buttons.accepted.connect(self.accept)
        root.addWidget(scroll, 1)
        root.addWidget(self._buttons)

        self._autostart.toggled.connect(self._on_autostart)

        self.retranslate()
        # 尺寸按内容的实际需求来：文案宽度随语言变（"Beim Schließen des Fensters"
        # 比「关闭窗口时」宽得多），写死一个值总会在某种语言下截断。
        # 滚动区会把 sizeHint 压小，所以量的是内部那个 holder。
        content = self._groups.sizeHint()
        self.setMinimumWidth(max(540, content.width() + 40))
        # 高度不许超过屏幕：超了交给滚动区，而不是把按钮顶出画面
        screen = self.screen()
        max_height = (int(screen.availableGeometry().height() * 0.92)
                      if screen is not None else 10000)
        self.resize(self.minimumWidth(),
                    min(content.height() + 90, max_height))  # +90 = 边距 + 按钮行
        # 先设好初值再连信号：否则构造期的 setCurrentIndex 会触发一次
        # _on_language，把 settings.json 无谓地重写一遍
        self._lang_combo.currentIndexChanged.connect(self._on_language)
        self._close_combo.currentIndexChanged.connect(self._on_close_action)

    # --- 语言 ---------------------------------------------------------------
    def retranslate(self) -> None:
        """按当前语言重设全部文案。幂等，切换语言后被调两次也无妨。"""
        self.setWindowTitle(tr("Settings"))
        self._lang_box.setTitle(tr("Language"))
        self._lang_combo.setItemText(self._lang_combo.findData(i18n.SYSTEM),
                                     i18n.language_name(i18n.SYSTEM))

        self._close_box.setTitle(tr("Closing the window"))
        for index in range(self._close_combo.count()):
            self._close_combo.setItemText(
                index, self._close_action_label(self._close_combo.itemData(index))
            )

        self._auto_box.setTitle(tr("Launch at login"))
        self._autostart.setText(tr("Start at login (tray mode)"))

        self._key_box.setTitle(tr("Password storage"))
        self._key_status.setText(f"● {self._secrets_status.label}")
        self._unlock.setText(tr("Unlock keyring"))
        detail = compose_detail(self._secrets_status, self._secrets_raw_detail)
        self._key_detail.setText(detail)
        self._key_detail.setVisible(bool(detail))

        self._env_box.setTitle(tr("Environment"))
        self._rebuild_env()

        self._about_box.setTitle(tr("About"))
        self._about.setText(self._about_text())

        self._buttons.button(QDialogButtonBox.StandardButton.Close).setText(tr("Close"))

    def _on_language(self, index: int) -> None:
        pref = self._lang_combo.itemData(index)
        ok, error = i18n.set_preference(pref)  # 立即生效 + 写盘
        if ok:
            self._lang_error.hide()
        else:
            # 写盘失败不阻止本次切换（与其它降级路径同一哲学），但要如实告知
            self._lang_error.setText("⚠ " + self._save_failed(error))
            self._lang_error.show()
        self.retranslate()

    def _on_close_action(self, index: int) -> None:
        ok, error = prefs.set_close_action(self._close_combo.itemData(index))
        if ok:
            self._close_error.hide()
        else:
            self._close_error.setText("⚠ " + self._save_failed(error))
            self._close_error.show()

    @staticmethod
    def _save_failed(error: str) -> str:
        return trf("Couldn't save the preference ({error}); "
                   "it stays in effect for this session only.", error=error)

    @staticmethod
    def _close_action_label(action: str) -> str:
        """下拉项文案。字面量放在这里，静态扫描才找得到这些 key。"""
        return tr({
            prefs.CLOSE_ASK: "Ask every time",
            prefs.CLOSE_TRAY: "Minimize to tray",
            prefs.CLOSE_QUIT: "Quit the program",
        }.get(action, "Ask every time"))

    # --- 组装 ---------------------------------------------------------------
    def _about_text(self) -> str:
        return (
            f"{tr(C.APP_NAME)} {C.APP_VERSION}<br>"
            f"krfb-virtualmonitor {tr(self._krfb_version_source)}<br><br>"  # i18n:dynamic
            f"{tr('Config:')} <code>{C.SCREENS_FILE}</code><br>"
            f"{tr('Runtime state:')} <code>{C.RUNTIME_FILE}</code><br>"
            f"{tr('Logs:')} <code>{C.LOG_DIR}</code>"
        )

    def _rebuild_env(self) -> None:
        """环境检查区整块重建。子控件必须先 setParent(None) 再 deleteLater()，
        否则在新内容上屏之前旧标签还会在原地显示一帧。"""
        while self._env_layout.count():
            item = self._env_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

        warnings = self._warnings_provider()
        if warnings:
            for text in warnings:
                item = QLabel("⚠  " + text)
                item.setWordWrap(True)
                item.setStyleSheet(f"color:{self._palette.color('warning').name()};")
                self._env_layout.addWidget(item)
        else:
            ok = QLabel(tr("No problems found"))
            ok.setWordWrap(True)
            ok.setStyleSheet(f"color:{self._palette.color('success').name()};")
            self._env_layout.addWidget(ok)

    def _on_autostart(self, enabled: bool) -> None:
        ok, error = autostart.set_enabled(enabled)
        if not ok:
            self._autostart_error.setText("⚠ " + error)
            self._autostart_error.show()
            self._autostart.blockSignals(True)
            self._autostart.setChecked(not enabled)
            self._autostart.blockSignals(False)
        else:
            self._autostart_error.hide()
