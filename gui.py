"""GUI приложения TEiL."""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTabWidget, QTextEdit, QScrollArea,
    QDialog, QCheckBox, QGroupBox, QFrame,
)
from PyQt6.QtCore import Qt, QEvent, pyqtSignal
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
    color: #89b4fa; font-weight: bold; padding: 4px 8px;
    background-color: #11111b; border-radius: 4px;
}
QLabel#sectionTitle { color: #a6e3a1; font-weight: bold; padding: 4px 2px; }
QLabel#preview {
    color: #a6e3a1; background-color: #11111b;
    padding: 6px 8px; border-radius: 4px;
    font-family: "Consolas", "DejaVu Sans Mono", monospace;
}
QLineEdit {
    background-color: #11111b; border: 1px solid #313244;
    border-radius: 4px; padding: 5px 8px; color: #cdd6f4;
}
QLineEdit:focus { border: 1px solid #89b4fa; }
QTextEdit#output {
    background-color: #11111b; border: 1px solid #313244;
    border-radius: 6px; padding: 8px; color: #a6e3a1;
    font-family: "Consolas", "DejaVu Sans Mono", monospace;
    font-size: 13px;
}
QTabWidget::pane {
    border: 1px solid #313244; border-radius: 6px;
    background: #181825;
}
QPushButton#tabButton {
    background-color: #181825;
    color: #bac2de;
    border: 1px solid #313244;
    border-radius: 4px;
    padding: 6px 14px;
    font-weight: normal;
    min-height: 22px;
    text-align: center;
}
QPushButton#tabButton:hover { background-color: #45475a; color: #cdd6f4; }
QPushButton#tabButton:checked {
    background-color: #313244; color: #89b4fa;
    border: 1px solid #89b4fa;
}
QPushButton#cmdBtn {
    background-color: #313244; color: #cdd6f4;
    border: 1px solid #45475a; border-radius: 4px;
    padding: 7px 10px; text-align: left;
}
QPushButton#cmdBtn:hover { background-color: #45475a; border: 1px solid #89b4fa; }
QPushButton#cmdBtn:pressed { background-color: #585b70; }
QPushButton#dangerBtn {
    background-color: #3a1e1e; color: #f38ba8;
    border: 1px solid #f38ba8; border-radius: 4px;
    padding: 7px 10px; text-align: left; font-weight: bold;
}
QPushButton#dangerBtn:hover { background-color: #5a2424; }
QPushButton#dangerBtn:pressed { background-color: #7a2e2e; }
QPushButton {
    background-color: #89b4fa; color: #11111b;
    border: none; border-radius: 4px;
    padding: 6px 14px; font-weight: bold;
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
QScrollBar:horizontal { background: #181825; height: 10px; margin: 0; }
QScrollBar::handle:horizontal {
    background: #45475a; border-radius: 5px; min-width: 20px;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
QGroupBox {
    border: 1px solid #313244; border-radius: 4px;
    margin-top: 10px; padding: 8px 6px 6px 6px; color: #bac2de;
}
QGroupBox::title {
    subcontrol-origin: margin; left: 8px; padding: 0 4px;
}
QCheckBox { color: #cdd6f4; padding: 2px; }
QCheckBox::indicator { width: 15px; height: 15px; }
"""


# ------------------------------------------------------------- drag-scroll area
class DragScrollArea(QScrollArea):
    DRAG_THRESHOLD = 8

    def __init__(self, parent=None):
        super().__init__(parent)
        self._dragging = False
        self._press_pos = None
        self._scroll_start = None
        self.viewport().installEventFilter(self)

    def setWidget(self, widget):
        super().setWidget(widget)
        self._install_filter_recursive(widget)

    def _install_filter_recursive(self, widget):
        widget.installEventFilter(self)
        for child in widget.findChildren(QWidget):
            child.installEventFilter(self)

    def eventFilter(self, obj, event):
        et = event.type()
        if et == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
            self._press_pos = event.globalPosition().toPoint()
            self._scroll_start = (
                self.horizontalScrollBar().value(),
                self.verticalScrollBar().value(),
            )
            self._dragging = False
        elif et == QEvent.Type.MouseMove:
            if self._press_pos is not None:
                delta = event.globalPosition().toPoint() - self._press_pos
                if not self._dragging and delta.manhattanLength() > self.DRAG_THRESHOLD:
                    self._dragging = True
                    self.viewport().setCursor(Qt.CursorShape.ClosedHandCursor)
                if self._dragging:
                    self.horizontalScrollBar().setValue(self._scroll_start[0] - delta.x())
                    self.verticalScrollBar().setValue(self._scroll_start[1] - delta.y())
                    return True
        elif et == QEvent.Type.MouseButtonRelease:
            was_dragging = self._dragging
            self._press_pos = None
            self._dragging = False
            self.viewport().unsetCursor()
            if was_dragging:
                return True
        return super().eventFilter(obj, event)


# ------------------------------------------------------------------ полоса категорий
class CategoryBar(QWidget):
    category_selected = pyqtSignal(int)

    def __init__(self, categories: list[str], parent=None):
        super().__init__(parent)
        self.setFixedHeight(46)
        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self.scroll = DragScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        hl = QHBoxLayout(container)
        hl.setContentsMargins(0, 0, 0, 0)
        hl.setSpacing(2)

        self.buttons: list[QPushButton] = []
        for i, name in enumerate(categories):
            btn = QPushButton(name)
            btn.setCheckable(True)
            btn.setObjectName("tabButton")
            btn.clicked.connect(lambda _=False, idx=i: self._select(idx))
            self.buttons.append(btn)
            hl.addWidget(btn)
        hl.addStretch()

        self.scroll.setWidget(container)
        outer.addWidget(self.scroll)

        if self.buttons:
            self.buttons[0].setChecked(True)

    def _select(self, idx: int):
        for i, btn in enumerate(self.buttons):
            btn.setChecked(i == idx)
        self.category_selected.emit(idx)


# ---------------------------------------------------------------------- диалог
def _is_single_letter_flag(flag: str) -> bool:
    return len(flag) == 2 and flag[0] == "-" and flag[1].isalpha()


class CommandDialog(QDialog):
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
            self.args_input.setPlaceholderText(
                cmd.get("arg_placeholder", "аргумент (опционально)")
            )
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
        ok_text = "Симулировать" if cmd.get("dangerous") else "Выполнить"
        ok = QPushButton(ok_text)
        ok.setDefault(True)
        ok.clicked.connect(self.accept)
        btns.addWidget(ok)
        layout.addLayout(btns)

        self._update_preview()

    def _update_preview(self):
        singles: list[str] = []
        others: list[str] = []
        for cb in self.flag_checks:
            if not cb.isChecked():
                continue
            t = cb.text()
            if _is_single_letter_flag(t):
                singles.append(t[1])
            else:
                others.append(t)

        parts = [self.cmd["name"]]
        if singles:
            parts.append("-" + "".join(sorted(singles)))
        parts.extend(others)

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
            "Категории и списки команд перетаскиваются мышкой.\n"
            "Однобуквенные ключи склеиваются: -l + -a + -h → -alh.\n"
            "touch в «Файлы и папки» — безопасный: создаёт файл только\n"
            "внутри текущей директории.\n"
            "Команды из категории «⚠ Опасные» НЕ выполняются — только симуляция.\n"
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

        left_panel = QWidget()
        left_panel.setMaximumWidth(380)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(6)

        self.category_bar = CategoryBar(list(CATEGORIES.keys()))
        left_layout.addWidget(self.category_bar)

        self.tabs = QTabWidget()
        self.tabs.tabBar().hide()
        self._build_tabs()
        left_layout.addWidget(self.tabs, 1)

        self.category_bar.category_selected.connect(self.tabs.setCurrentIndex)

        main_area.addWidget(left_panel)

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
            scroll = DragScrollArea()
            scroll.setWidgetResizable(True)
            inner = QWidget()
            v = QVBoxLayout(inner)
            v.setSpacing(6)
            v.setContentsMargins(6, 6, 6, 6)

            for cmd in commands:
                btn = QPushButton(cmd["name"])
                btn.setToolTip(cmd.get("desc", ""))
                btn.setObjectName("dangerBtn" if cmd.get("dangerous") else "cmdBtn")
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

        # 1) безопасные встроенные обработчики
        handler = cmd.get("safe_handler")
        if handler == "touch":
            target = full_cmd[len("touch"):].strip()
            self._append_output(self.executor.safe_touch(target))
            return

        # 2) cd — меняем директорию
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

        # 3) опасные — только симуляция
        if cmd.get("dangerous"):
            sim = cmd["sim"](full_cmd) if callable(cmd.get("sim")) else cmd.get("sim", "")
            self._append_output(
                "⚠ ОПАСНАЯ КОМАНДА — реальное выполнение запрещено.\n" + sim
            )
            return

        # 4) всё остальное — реальное выполнение
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