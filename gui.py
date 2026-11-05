"""GUI приложения TEiL."""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTabWidget, QTextEdit, QScrollArea,
    QDialog, QCheckBox, QGroupBox,
)
from PyQt6.QtGui import QTextCursor

from commands import CATEGORIES, CommandExecutor


STYLESHEET = """
QMainWindow, QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-family: "Consolas", "DejaVu Sans Mono", "Courier New", monospace;
    font-size: 13px;
}
QLabel#cwdLabel {
    color: #89b4fa;
    font-weight: bold;
    padding: 4px 8px;
    background-color: #11111b;
    border-radius: 4px;
}
QLabel#sectionTitle {
    color: #a6e3a1;
    font-weight: bold;
    padding: 4px 2px;
}
QLabel#preview {
    color: #a6e3a1;
    background-color: #11111b;
    padding: 6px 8px;
    border-radius: 4px;
    font-family: "Consolas", "DejaVu Sans Mono", monospace;
}
QLineEdit {
    background-color: #11111b;
    border: 1px solid #313244;
    border-radius: 4px;
    padding: 5px 8px;
    color: #cdd6f4;
}
QLineEdit:focus { border: 1px solid #89b4fa; }
QTextEdit#output {
    background-color: #11111b;
    border: 1px solid #313244;
    border-radius: 6px;
    padding: 8px;
    color: #a6e3a1;
    font-family: "Consolas", "DejaVu Sans Mono", monospace;
    font-size: 13px;
}
QTabWidget::pane {
    border: 1px solid #313244;
    border-radius: 6px;
    background: #181825;
}
QTabBar::tab {
    background: #181825;
    color: #bac2de;
    padding: 6px 12px;
    border: 1px solid #313244;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    margin-right: 2px;
}
QTabBar::tab:selected { background: #313244; color: #89b4fa; }
QTabBar::tab:hover { background: #45475a; }
QPushButton#cmdBtn {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 4px;
    padding: 7px 10px;
    text-align: left;
}
QPushButton#cmdBtn:hover { background-color: #45475a; border: 1px solid #89b4fa; }
QPushButton#cmdBtn:pressed { background-color: #585b70; }
QPushButton#dangerBtn {
    background-color: #3a1e1e;
    color: #f38ba8;
    border: 1px solid #f38ba8;
    border-radius: 4px;
    padding: 7px 10px;
    text-align: left;
    font-weight: bold;
}
QPushButton#dangerBtn:hover { background-color: #5a2424; }
QPushButton#dangerBtn:pressed { background-color: #7a2e2e; }
QPushButton {
    background-color: #89b4fa;
    color: #11111b;
    border: none;
    border-radius: 4px;
    padding: 6px 14px;
    font-weight: bold;
}
QPushButton:hover { background-color: #74a8f7; }
QPushButton:pressed { background-color: #5b93e6; }
QScrollArea { border: none; background: #181825; }
QScrollBar:vertical { background: #181825; width: 10px; margin: 0; }
QScrollBar::handle:vertical {
    background: #45475a; border-radius: 5px; min-height: 20px;
}
QScrollBar::handle:vertical:hover { background: #585b70; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QGroupBox {
    border: 1px solid #313244;
    border-radius: 4px;
    margin-top: 10px;
    padding: 8px 6px 6px 6px;
    color: #bac2de;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 8px;
    padding: 0 4px;
}
QCheckBox { color: #cdd6f4; padding: 2px; }
QCheckBox::indicator { width: 15px; height: 15px; }
"""


def _is_single_letter_flag(flag: str) -> bool:
    """True для -a, -l, -h, -R и т.п. Такие флаги склеиваются."""
    return len(flag) == 2 and flag[0] == "-" and flag[1].isalpha()


# ---------------------------------------------------------------------- диалог
class CommandDialog(QDialog):
    """Диалог выбора ключей и ввода аргумента для конкретной команды."""

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

        # чек-боксы ключей
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

        # поле аргумента
        if cmd.get("arg_placeholder") or flags:
            layout.addWidget(QLabel("Аргумент:"))
            self.args_input = QLineEdit()
            self.args_input.setPlaceholderText(
                cmd.get("arg_placeholder", "аргумент (опционально)")
            )
            self.args_input.textChanged.connect(self._update_preview)
            self.args_input.returnPressed.connect(self.accept)
            layout.addWidget(self.args_input)
        else:
            self.args_input = None

        # предпросмотр
        layout.addWidget(QLabel("Итоговая команда:"))
        self.preview = QLabel()
        self.preview.setObjectName("preview")
        self.preview.setWordWrap(True)
        layout.addWidget(self.preview)

        # кнопки
        btns = QHBoxLayout()
        btns.addStretch(1)
        cancel = QPushButton("Отмена")
        cancel.clicked.connect(self.reject)
        btns.addWidget(cancel)

        ok_text = "Симулировать" if cmd.get("dangerous") else "Выполнить"
        ok = QPushButton(ok_text)
        ok.setDefault(True)
        ok.clicked.connect(self.accept)
        btns.addWidget(ok)
        layout.addLayout(btns)

        self._update_preview()

    def _update_preview(self):
        # собираем выбранные флаги
        single_letters: list[str] = []
        other_flags: list[str] = []
        for cb in self.flag_checks:
            if not cb.isChecked():
                continue
            text = cb.text()
            if _is_single_letter_flag(text):
                single_letters.append(text[1])
            else:
                other_flags.append(text)

        parts = [self.cmd["name"]]

        # -a + -l + -h -> -alh (сортируем для предсказуемости)
        if single_letters:
            parts.append("-" + "".join(sorted(single_letters)))

        # многословные/неоднобуквенные — как есть
        parts.extend(other_flags)

        # аргумент в конце
        if self.args_input is not None:
            args = self.args_input.text().strip()
            if args:
                parts.append(args)

        self.full_command = " ".join(parts)
        self.preview.setText(f"$ {self.full_command}")

    def get_command(self) -> str:
        return self.full_command


# ---------------------------------------------------------------- главное окно
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TEiL — Terminal Emulator in Linux")
        self.resize(1150, 720)
        self.setStyleSheet(STYLESHEET)

        self.executor = CommandExecutor()
        self._build_ui()
        self._update_cwd()

        self._append_output(
            "Добро пожаловать в TEiL — эмулятор терминала Linux.\n"
            "Нажмите кнопку команды, отметьте нужные ключи и введите аргумент.\n"
            "Однобуквенные ключи склеиваются автоматически: "
            "-l + -a + -h → -alh.\n"
            "Команды из категории «⚠ Опасные» НЕ выполняются — "
            "показывается только симуляция вывода.\n"
        )

    # ------------------------------------------------------------------ UI
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(8)

        header = QHBoxLayout()
        header.addWidget(QLabel("Текущая директория:"))
        self.cwd_label = QLabel()
        self.cwd_label.setObjectName("cwdLabel")
        header.addWidget(self.cwd_label, 1)
        root.addLayout(header)

        main_area = QHBoxLayout()

        self.tabs = QTabWidget()
        self.tabs.setMaximumWidth(360)
        self._build_tabs()
        main_area.addWidget(self.tabs)

        right = QVBoxLayout()
        title = QLabel("Результат выполнения:")
        title.setObjectName("sectionTitle")
        right.addWidget(title)

        self.output = QTextEdit()
        self.output.setObjectName("output")
        self.output.setReadOnly(True)
        right.addWidget(self.output, 1)

        clear_btn = QPushButton("Очистить вывод")
        clear_btn.clicked.connect(self.output.clear)
        right.addWidget(clear_btn)

        main_area.addLayout(right, 1)
        root.addLayout(main_area, 1)

    def _build_tabs(self):
        for category, commands in CATEGORIES.items():
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            inner = QWidget()
            v = QVBoxLayout(inner)
            v.setSpacing(6)
            v.setContentsMargins(6, 6, 6, 6)

            for cmd in commands:
                btn = QPushButton(cmd["name"])
                btn.setToolTip(cmd.get("desc", ""))
                btn.setObjectName(
                    "dangerBtn" if cmd.get("dangerous") else "cmdBtn"
                )
                btn.clicked.connect(
                    lambda _=False, c=cmd: self._on_command_clicked(c)
                )
                v.addWidget(btn)

            v.addStretch(1)
            scroll.setWidget(inner)
            self.tabs.addTab(scroll, category)

    # ------------------------------------------------------------- actions
    def _on_command_clicked(self, cmd: dict):
        if cmd.get("instant"):
            self._execute(cmd["name"], cmd)
            return

        dlg = CommandDialog(cmd, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._execute(dlg.get_command(), cmd)

    def _execute(self, full_cmd: str, cmd: dict):
        self._append_output(f"\n$ {full_cmd}")

        if cmd["name"] == "cd":
            target = full_cmd[len("cd"):].strip()
            if not target:
                self._append_output(self.executor.cwd)
            else:
                ok, err = self.executor.change_dir(target)
                if ok:
                    self._update_cwd()
                else:
                    self._append_output(err)
            return

        if cmd.get("dangerous"):
            sim = cmd["sim"](full_cmd) if callable(cmd.get("sim")) else cmd.get("sim", "")
            self._append_output(
                "⚠ ОПАСНАЯ КОМАНДА — реальное выполнение запрещено.\n" + sim
            )
            return

        self._append_output(self.executor.execute(full_cmd))

    # ------------------------------------------------------------- helpers
    def _update_cwd(self):
        self.cwd_label.setText(self.executor.cwd)

    def _append_output(self, text: str):
        if not text.endswith("\n"):
            text += "\n"
        self.output.moveCursor(QTextCursor.MoveOperation.End)
        self.output.insertPlainText(text)
        self.output.moveCursor(QTextCursor.MoveOperation.End)