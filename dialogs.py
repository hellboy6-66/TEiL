"""Диалоговые окна приложения TEiL."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QCheckBox, QGroupBox, QTextBrowser
)
from PyQt6.QtCore import Qt, pyqtSignal
from manual import MANUAL_DATA

def _is_single_letter_flag(flag: str) -> bool:
    return len(flag) == 2 and flag[0] == "-" and flag[1].isalpha()


class CommandDialog(QDialog):
    """Диалог настройки и ввода команды."""
    def __init__(self, cmd: dict, parent=None):
        super().__init__(parent)
        self.cmd = cmd
        self.full_command = cmd["name"]
        self.setWindowTitle(f"TEiL — {cmd['name']}")
        self.setMinimumWidth(440)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        
        desc = QLabel(cmd.get("desc", ""))
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        self.flag_checks: list[QCheckBox] = []
        flags = cmd.get("flags", [])
        if flags:
            group = QGroupBox("Ключи (однобуквенные склеиваются в один флаг)")
            gl = QVBoxLayout(group)
            gl.setSpacing(4)
            for flag in flags:
                cb = QCheckBox(flag)
                cb.stateChanged.connect(self._update_preview)
                gl.addWidget(cb)
                self.flag_checks.append(cb)
            layout.addWidget(group)
            
        if cmd.get("arg_placeholder") or flags:
            layout.addWidget(QLabel("Аргумент:"))
            self.args_input = QLineEdit()
            self.args_input.setPlaceholderText(cmd.get("arg_placeholder", "аргумент (опционально)"))
            self.args_input.textChanged.connect(self._update_preview)
            self.args_input.returnPressed.connect(self.accept)
            layout.addWidget(self.args_input)
        else:
            self.args_input = None
            
        layout.addWidget(QLabel("Итоговая команда:"))
        self.preview = QLabel()
        self.preview.setObjectName("preview")
        self.preview.setWordWrap(True)
        layout.addWidget(self.preview)
        
        btns = QHBoxLayout()
        btns.addStretch(1)
        cancel = QPushButton("Отмена")
        cancel.clicked.connect(self.reject)
        btns.addWidget(cancel)
        ok = QPushButton("Выполнить")
        ok.setDefault(True)
        ok.clicked.connect(self.accept)
        btns.addWidget(ok)
        layout.addLayout(btns)
        
        self._update_preview()

    def _update_preview(self):
        singles, others = [], []
        for cb in self.flag_checks:
            if not cb.isChecked(): continue
            t = cb.text()
            if _is_single_letter_flag(t): singles.append(t[1])
            else: others.append(t)
        parts = [self.cmd["name"]]
        if singles: parts.append("-" + "".join(sorted(singles)))
        parts.extend(others)
        if self.args_input is not None:
            args = self.args_input.text().strip()
            if args: parts.append(args)
        self.full_command = " ".join(parts)
        self.preview.setText(f"$ {self.full_command}")

    def get_command(self) -> str: 
        return self.full_command


class HelpDialog(QDialog):
    """Окно справочника по командам Linux."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("TEiL — Справочник команд Linux")
        self.resize(750, 600)
        layout = QVBoxLayout(self)

        browser = QTextBrowser()
        html = "<html><body style='font-family: Consolas, monospace; font-size: 14px;'>"
        for block in MANUAL_DATA:
            html += f"<h2 style='color: #89b4fa;'>{block['category']}</h2><ul>"
            for item in block['commands']:
                html += f"<li style='margin-bottom: 12px;'>"
                html += f"<b style='color: #a6e3a1;'>{item['cmd']}</b><br>"
                html += f"<span style='color: #cdd6f4;'>{item['desc'].replace(chr(10), '<br>')}</span>"
                html += "</li>"
            html += "</ul><hr>"
        html += "</body></html>"
        
        browser.setHtml(html)
        layout.addWidget(browser)

        btn_close = QPushButton("Закрыть")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close, alignment=Qt.AlignmentFlag.AlignRight)


class SettingsDialog(QDialog):
    """Окно настроек приложения."""
    theme_changed = pyqtSignal(bool)

    def __init__(self, is_light: bool, parent=None):
        super().__init__(parent)
        self.setWindowTitle("TEiL — Настройки")
        self.setMinimumWidth(350)
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        theme_group = QGroupBox("Оформление")
        tl = QVBoxLayout(theme_group)
        self.light_cb = QCheckBox("Светлая тема")
        self.light_cb.setChecked(is_light)
        self.light_cb.stateChanged.connect(self._on_theme_toggled)
        tl.addWidget(self.light_cb)
        layout.addWidget(theme_group)

        help_group = QGroupBox("Помощь")
        hl = QVBoxLayout(help_group)
        btn_manual = QPushButton("Открыть справочник команд")
        btn_manual.clicked.connect(self._open_manual)
        hl.addWidget(btn_manual)
        layout.addWidget(help_group)

        layout.addStretch()
        
        btns = QHBoxLayout()
        btns.addStretch(1)
        btn_close = QPushButton("Закрыть")
        btn_close.clicked.connect(self.accept)
        btns.addWidget(btn_close)
        layout.addLayout(btns)

    def _on_theme_toggled(self):
        self.theme_changed.emit(self.light_cb.isChecked())

    def _open_manual(self):
        dlg = HelpDialog(self)
        dlg.exec()