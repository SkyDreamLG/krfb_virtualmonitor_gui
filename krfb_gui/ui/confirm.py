"""高危操作的确认：警告弹窗 + 算术验证码。

**算术验证码是防手滑的，不是安全控制** —— 它挡的是"看都没看就点确定"，
挡不住任何有意为之的人（题目和答案都在同一个进程里）。真要保护数据得靠加密，
不要拿它当门禁。这一点在代码和界面文案里都如实说明。

只用在**密码库级别**的操作上：重置内置库、清除原密码库的数据、丢弃数据。
删虚拟屏维持原来的警告弹窗（那是日常操作，加验证码太烦）。

弹窗按钮文字一律自己设：Qt 自带的 `qtbase_*.qm` 不随本程序分发，
用标准按钮的话在非英文系统上会露出英文。
"""

from __future__ import annotations

import secrets as _secrets

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from ..i18n import tr, trf
from .theme import Palette


class ArithmeticGate(QDialog):
    """让用户算一道两位数加法，答对才能继续。"""

    def __init__(self, palette: Palette, *, title: str, text: str,
                 attempts: int = 3, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._attempts = attempts
        self._expected = 0
        self.setWindowTitle(title)
        self.setMinimumWidth(360)

        self._text = QLabel(text)
        self._text.setWordWrap(True)

        self._question = QLabel()
        self._question.setStyleSheet("font-weight: 600; font-size: 15px;")

        self._answer = QLineEdit()
        self._answer.setPlaceholderText(tr("Type the result here"))

        self._error = QLabel()
        self._error.setWordWrap(True)
        self._error.setStyleSheet(f"color:{palette.color('danger').name()};")

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText(tr("Confirm"))
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText(tr("Cancel"))
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)

        row = QHBoxLayout()
        row.addWidget(self._question)
        row.addWidget(self._answer, 1)

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 16, 18, 14)
        root.setSpacing(11)
        root.addWidget(self._text)
        root.addLayout(row)
        root.addWidget(self._error)
        root.addWidget(buttons)

        self._new_question()
        self._answer.setFocus(Qt.FocusReason.OtherFocusReason)

    def _new_question(self) -> None:
        a = _secrets.choice(range(11, 100))
        b = _secrets.choice(range(11, 100))
        self._expected = a + b
        self._question.setText(trf("{a} + {b} = ?", a=a, b=b))
        self._answer.clear()

    def _on_accept(self) -> None:
        raw = self._answer.text().strip()
        if raw.isdigit() and int(raw) == self._expected:
            self.accept()
            return

        self._attempts -= 1
        if self._attempts <= 0:
            self._error.setText(tr("Too many wrong answers"))
            self.reject()
            return
        self._error.setText(tr("Wrong answer, here is another one"))
        self._new_question()
        self._answer.setFocus(Qt.FocusReason.OtherFocusReason)


def destructive_action(parent: QWidget, palette: Palette, *, title: str, text: str,
                       informative: str, confirm_label: str) -> bool:
    """两段确认：先警告，再算一道题。两段都过才返回 True。

    `title` / `text` / `informative` / `confirm_label` 由调用方给**已翻译**的
    字符串（字面量留在调用点，静态扫描才找得到）。
    """
    box = QMessageBox(parent)
    box.setWindowTitle(title)
    box.setIcon(QMessageBox.Icon.Warning)
    box.setText(text)
    if informative:
        box.setInformativeText(informative)
    confirm = box.addButton(confirm_label, QMessageBox.ButtonRole.DestructiveRole)
    box.addButton(tr("Cancel"), QMessageBox.ButtonRole.RejectRole)
    box.setDefaultButton(box.buttons()[-1])   # 默认落在"取消"上
    box.exec()
    if box.clickedButton() is not confirm:
        return False

    gate = ArithmeticGate(palette, title=title, text=text, parent=parent)
    return gate.exec() == QDialog.DialogCode.Accepted


def choose_store_data(parent: QWidget, *, target: str, source: str, count: int,
                      when: str, moving: int) -> str:
    """目标密码库已有数据时：保留目标的 / 用新数据覆盖 / 合并 / 取消。

    返回 `"target"` / `"source"` / `"merge"` / `"cancel"`。

    这里**不**再加算术验证码：三个按钮本身就是把后果写在脸上的选择
    （而验证码只用来挡"看都没看就点确定"的高危清库操作，见模块 docstring）。
    """
    box = QMessageBox(parent)
    box.setWindowTitle(tr("Password store"))
    box.setIcon(QMessageBox.Icon.Warning)
    box.setText(trf("{store} already holds {count} of this app's passwords ({when}).",
                    store=target, count=count, when=when))
    box.setInformativeText(
        trf("{source} holds {moving} for the same screens. "
            "Whichever side you drop is deleted for good.",
            source=source, moving=moving))
    keep = box.addButton(tr("Keep the target's passwords"),
                         QMessageBox.ButtonRole.AcceptRole)
    overwrite = box.addButton(tr("Overwrite with the new passwords"),
                              QMessageBox.ButtonRole.DestructiveRole)
    merge = box.addButton(tr("Merge…"), QMessageBox.ButtonRole.ActionRole)
    box.addButton(tr("Cancel"), QMessageBox.ButtonRole.RejectRole)
    box.setDefaultButton(keep)      # 默认落在"不动数据"上
    box.exec()
    clicked = box.clickedButton()
    if clicked is overwrite:
        return "source"
    if clicked is merge:
        return "merge"
    if clicked is keep:
        return "target"
    return "cancel"


def choose_merge_rule(parent: QWidget, *, adding: int, identical: int,
                      conflicts: int, names: str = "") -> bool | None:
    """冲突怎么收场。返回 True=冲突时用新数据，False=冲突时保留目标的，None=取消。"""
    box = QMessageBox(parent)
    box.setWindowTitle(tr("Merge"))
    box.setIcon(QMessageBox.Icon.Question)
    box.setText(trf("{adding} will be added, {identical} are identical and "
                    "will be skipped, {conflicts} conflict.",
                    adding=adding, identical=identical, conflicts=conflicts))
    if names:
        box.setInformativeText(trf("Screens in conflict: {names}", names=names))
    keep = box.addButton(tr("Keep the target's version"),
                         QMessageBox.ButtonRole.AcceptRole)
    use_new = box.addButton(tr("Use the new version"),
                            QMessageBox.ButtonRole.DestructiveRole)
    box.addButton(tr("Cancel"), QMessageBox.ButtonRole.RejectRole)
    box.setDefaultButton(keep)
    box.exec()
    clicked = box.clickedButton()
    if clicked is use_new:
        return True
    if clicked is keep:
        return False
    return None
