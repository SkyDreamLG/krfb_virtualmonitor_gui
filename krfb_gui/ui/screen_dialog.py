"""新建 / 编辑虚拟屏对话框。

两个刻意的设计：

  * 底部实时显示**将要执行的完整命令行**。这样用户既能看到 GUI 到底做了什么，
    也能直接把命令复制走自己用 —— 这个程序本来就该是命令行的一层便利封装，
    而不是一个黑盒。
  * 密码明文长度提示到 8 位为止，因为 VNC 的 DES 认证只取前 8 个字符，
    更长的密码不会增加安全性，界面必须如实说明。
"""

from __future__ import annotations

import uuid

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from .. import constants as C
from ..i18n import tr, trf
from ..manager import command_preview
from ..models import Screen
from ..proctools import port_in_use
from ..secrets import effective_length, generate_password
from ..store import Store
from . import icons
from .theme import Palette
from .vector import AspectPreview, DrawIcon


class ScreenDialog(QDialog):
    """返回值通过 `result_screen` 取出。"""

    def __init__(self, palette: Palette, store: Store, screen: Screen | None = None,
                 password: str | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._palette = palette
        self._store = store
        self._editing = screen
        self._port_ok = True
        # 新建时用一个稳定的 id，避免每次刷新都生成新的 uuid
        self._new_id = str(uuid.uuid4())

        self.setWindowTitle(tr("Edit virtual screen") if screen else tr("New virtual screen"))
        self.setModal(True)
        self.setMinimumWidth(520)

        self._name = QLineEdit(screen.name if screen else "")
        self._name.setPlaceholderText(tr(
            "e.g. Tablet (it becomes the KWin output \"Virtual-<name>\")"
        ))

        self._preset = QComboBox()
        for width, height, note in C.RESOLUTION_PRESETS:
            # note 来自 constants.RESOLUTION_PRESETS 的常量表：只有 "3:2 Tablet"
            # 有中文词条，其余（720p / 4K…）是通用写法，原样透传
            label = tr(note)  # i18n:dynamic
            self._preset.addItem(f"{width} × {height}   {label}", (width, height))
        self._preset.addItem(tr("Custom…"), None)

        self._width = QSpinBox()
        self._width.setRange(C.RESOLUTION_MIN, C.RESOLUTION_MAX)
        self._height = QSpinBox()
        self._height.setRange(C.RESOLUTION_MIN, C.RESOLUTION_MAX)

        self._scale = QDoubleSpinBox()
        self._scale.setRange(C.SCALE_MIN, C.SCALE_MAX)
        self._scale.setSingleStep(0.25)
        self._scale.setDecimals(2)
        self._scale.setSuffix(" ×")

        self._port = QSpinBox()
        self._port.setRange(C.PORT_MIN, C.PORT_MAX)
        self._auto_port = QPushButton(tr("Auto"))
        self._auto_port.setToolTip(tr("Pick a port that is neither in use "
                                      "nor assigned to another virtual screen"))
        self._port_icon = DrawIcon(palette, "check", 18)

        self._password = QLineEdit(password or generate_password())
        self._password.setEchoMode(QLineEdit.EchoMode.Password)
        self._reveal = QPushButton()
        self._reveal.setCheckable(True)
        icons.mark_icon_only(self._reveal)
        self._reveal.setFixedSize(32, 30)
        self._reveal.setIcon(icons.icon("eye", palette.color("text_dim"), 15))
        self._reveal.setToolTip(tr("Show / hide the password"))
        self._generate = QPushButton(tr("Random"))
        self._copy_pw = QPushButton()
        icons.mark_icon_only(self._copy_pw)
        self._copy_pw.setFixedSize(32, 30)
        self._copy_pw.setIcon(icons.icon("copy", palette.color("text_dim"), 15))
        self._copy_pw.setToolTip(tr("Copy the password"))

        self._password_hint = QLabel()
        self._password_hint.setProperty("role", "faint")
        self._password_hint.setWordWrap(True)

        self._notes = QLineEdit(screen.notes if screen else "")
        self._notes.setPlaceholderText(tr("Optional, e.g. \"second screen for the iPad\""))

        self._desired = QCheckBox(tr("Start at login"))
        self._desired.setChecked(screen.desired_running if screen else False)

        self._preview = AspectPreview(palette)
        self._command = QLabel()
        self._command.setProperty("role", "mono")
        self._command.setWordWrap(True)
        self._command.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self._command.setStyleSheet(
            f"background:{palette.color('surface_alt').name()};"
            f"border:1px solid {palette.color('border').name()};"
            f"border-radius:7px; padding:8px 10px;"
        )

        self._buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self._buttons.button(QDialogButtonBox.StandardButton.Ok).setText(tr("Save"))
        self._buttons.button(QDialogButtonBox.StandardButton.Ok).setProperty("accent", True)
        self._buttons.button(QDialogButtonBox.StandardButton.Cancel).setText(tr("Cancel"))
        self._buttons.accepted.connect(self._on_accept)
        self._buttons.rejected.connect(self.reject)

        self._build_layout()
        self._wire()

        # 初始化值
        if screen:
            self._width.setValue(screen.width)
            self._height.setValue(screen.height)
            self._scale.setValue(screen.scale)
            self._port.setValue(screen.port)
            self._sync_preset_from_size()
        else:
            self._width.setValue(C.DEFAULT_RESOLUTION[0])
            self._height.setValue(C.DEFAULT_RESOLUTION[1])
            self._scale.setValue(C.DEFAULT_SCALE)
            suggested = store.next_free_port()
            self._port.setValue(suggested if suggested else C.DEFAULT_PORT)
            self._sync_preset_from_size()

        self._refresh()
        # 标签列宽度随语言变（"Resolution" 比「分辨率」宽），写死 520 会在
        # 英文下把标签截断 —— 用内容自己的最小需求兜底
        self.setMinimumWidth(max(520, self.minimumSizeHint().width()))

    # --- 布局 ---------------------------------------------------------------
    def _build_layout(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 16)
        root.setSpacing(13)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        form.addRow(tr("Name"), self._name)

        size_row = QHBoxLayout()
        size_row.setSpacing(7)
        size_row.addWidget(self._preset, 1)
        size_row.addWidget(self._width)
        x_label = QLabel("×")
        x_label.setProperty("role", "dim")
        size_row.addWidget(x_label)
        size_row.addWidget(self._height)
        form.addRow(tr("Resolution"), size_row)

        scale_row = QHBoxLayout()
        scale_row.setSpacing(7)
        scale_row.addWidget(self._scale, 0)
        scale_row.addStretch(1)
        form.addRow(tr("Scale DPR"), scale_row)

        port_row = QHBoxLayout()
        port_row.setSpacing(7)
        port_row.addWidget(self._port, 0)
        port_row.addWidget(self._port_icon, 0)
        port_row.addWidget(self._auto_port, 0)
        port_row.addStretch(1)
        form.addRow(tr("Port"), port_row)

        pw_row = QHBoxLayout()
        pw_row.setSpacing(6)
        pw_row.addWidget(self._password, 1)
        pw_row.addWidget(self._reveal, 0)
        pw_row.addWidget(self._generate, 0)
        pw_row.addWidget(self._copy_pw, 0)
        form.addRow(tr("Password"), pw_row)

        form.addRow("", self._password_hint)
        form.addRow(tr("Notes"), self._notes)
        form.addRow("", self._desired)

        root.addLayout(form)
        root.addWidget(self._preview)

        cmd_caption = QLabel(tr("Command that will be executed"))
        cmd_caption.setProperty("role", "dim")
        root.addWidget(cmd_caption)
        root.addWidget(self._command)
        root.addWidget(self._buttons)

    def _wire(self) -> None:
        self._name.textChanged.connect(self._refresh)
        self._preset.currentIndexChanged.connect(self._on_preset)
        self._width.valueChanged.connect(self._on_size_edited)
        self._height.valueChanged.connect(self._on_size_edited)
        self._scale.valueChanged.connect(self._refresh)
        self._port.valueChanged.connect(self._refresh)
        self._password.textChanged.connect(self._refresh)
        self._notes.textChanged.connect(self._refresh)
        self._desired.toggled.connect(self._refresh)

        self._auto_port.clicked.connect(self._on_auto_port)
        self._reveal.toggled.connect(self._on_reveal)
        self._generate.clicked.connect(self._on_generate)
        self._copy_pw.clicked.connect(self._on_copy)

    # --- 事件 ---------------------------------------------------------------
    def _on_preset(self) -> None:
        data = self._preset.currentData()
        if data is None:
            return
        width, height = data
        self._width.blockSignals(True)
        self._height.blockSignals(True)
        self._width.setValue(width)
        self._height.setValue(height)
        self._width.blockSignals(False)
        self._height.blockSignals(False)
        self._refresh()

    def _on_size_edited(self) -> None:
        self._sync_preset_from_size()
        self._refresh()

    def _sync_preset_from_size(self) -> None:
        """宽高与某个预设一致时，下拉框跟着选中它；否则切到「自定义」。"""
        current = (self._width.value(), self._height.value())
        self._preset.blockSignals(True)
        for index in range(self._preset.count()):
            if self._preset.itemData(index) == current:
                self._preset.setCurrentIndex(index)
                break
        else:
            self._preset.setCurrentIndex(self._preset.count() - 1)
        self._preset.blockSignals(False)

    def _on_auto_port(self) -> None:
        free = self._store.next_free_port()
        if free is not None:
            self._port.setValue(free)

    def _on_reveal(self, shown: bool) -> None:
        self._password.setEchoMode(
            QLineEdit.EchoMode.Normal if shown else QLineEdit.EchoMode.Password
        )
        self._reveal.setIcon(icons.icon(
            "eye-off" if shown else "eye", self._palette.color("text_dim"), 15
        ))

    def _on_generate(self) -> None:
        self._password.setText(generate_password())

    def _on_copy(self) -> None:
        from PySide6.QtWidgets import QApplication

        QApplication.clipboard().setText(self._password.text())
        self._copy_pw.setIcon(icons.icon("check", self._palette.color("success"), 15))
        from PySide6.QtCore import QTimer

        QTimer.singleShot(1100, lambda: self._copy_pw.setIcon(
            icons.icon("copy", self._palette.color("text_dim"), 15)
        ))

    # --- 状态刷新 -----------------------------------------------------------
    def _draft(self) -> Screen:
        return Screen(
            name=self._name.text().strip(),
            width=self._width.value(),
            height=self._height.value(),
            scale=self._scale.value(),
            port=self._port.value(),
            notes=self._notes.text().strip(),
            desired_running=self._desired.isChecked(),
            id=self._editing.id if self._editing else self._new_id,
        )

    def _refresh(self) -> None:
        draft = self._draft()
        name = draft.name

        # --- 名称校验 ---
        exclude = self._editing.id if self._editing else None
        if not name:
            self._name.setStyleSheet(f"border-color: {self._palette.color('danger').name()};")
            name_error = tr("The name can't be empty")
        elif self._store.name_taken(name, exclude_id=exclude):
            self._name.setStyleSheet(f"border-color: {self._palette.color('danger').name()};")
            name_error = trf('"{name}" is already in use '
                             "(the KWin output name Virtual-{name} must be unique)",
                             name=name)
        else:
            self._name.setStyleSheet("")
            name_error = ""

        # --- 端口校验 ---
        if self._store.port_taken(draft.port, exclude_id=exclude):
            self._port_ok = False
            port_error = trf("Port {port} is already used by another virtual screen",
                             port=draft.port)
        elif port_in_use(draft.port):
            self._port_ok = False
            port_error = trf("Port {port} is already taken by another program on the system",
                             port=draft.port)
        else:
            self._port_ok = True
            port_error = ""

        if port_error:
            self._port_icon.show_state("cross", self._palette.color("danger"))
        else:
            self._port_icon.show_state("check", self._palette.color("success"))

        # --- 密码提示 ---
        password = self._password.text()
        if not password:
            hint = tr("The password can't be empty")
            tone = self._palette.color("danger").name()
        else:
            used = effective_length(password)
            if len(password) > C.VNC_PASSWORD_LEN:
                hint = trf("VNC authentication only uses the first 8 characters; "
                           "the remaining {extra} have no effect "
                           "(effective password: {effective})",
                           extra=len(password) - used,
                           effective=password[:C.VNC_PASSWORD_LEN])
            else:
                hint = tr("VNC authentication uses all 8 characters")
            tone = self._palette.color("text_faint").name()
        self._password_hint.setText(hint)
        self._password_hint.setStyleSheet(f"color: {tone};")

        # --- 命令预览 ---
        self._command.setText(command_preview(draft, password, mask=True))

        # --- 矢量预览 ---
        self._preview.set_resolution(
            draft.width, draft.height, draft.resolution_display, f"@{draft.scale:g}x"
        )

        # --- 确定按钮 ---
        ok_button = self._buttons.button(QDialogButtonBox.StandardButton.Ok)
        ok_button.setEnabled(not name_error and self._port_ok and bool(password))
        ok_button.setToolTip(name_error or port_error)

    def _on_accept(self) -> None:
        draft = self._draft()
        if self._editing:
            self._editing.name = draft.name
            self._editing.width = draft.width
            self._editing.height = draft.height
            self._editing.scale = draft.scale
            self._editing.port = draft.port
            self._editing.notes = draft.notes
            self._editing.desired_running = draft.desired_running
            self.result_screen = self._editing
        else:
            self.result_screen = draft
        self.result_password = self._password.text()
        self.accept()

    result_screen: Screen | None = None
    result_password: str = ""
