"""GUI приложения TEiL."""

import os
import json
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTabWidget, QTextEdit, QScrollArea,
    QDialog, QCheckBox, QGroupBox, QFrame, QMessageBox, QTextBrowser,
    QApplication, QStackedWidget
)
from PyQt6.QtCore import Qt, QEvent, pyqtSignal
from PyQt6.QtGui import QTextCursor

from commands import CATEGORIES, CommandExecutor
from manual import MANUAL_DATA

# Путь к файлу настроек (создастся в папке с программой)
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "teili_config.json")


DARK_STYLESHEET = """
QMainWindow, QWidget {
    background-color: #1e1e2e; color: #cdd6f4;
    font-family: "Consolas", "DejaVu Sans Mono", "Courier New", monospace; font-size: 13px;
}
QLabel#cwdLabel { color: #89b4fa; font-weight: bold; padding: 4px 8px; background-color: #11111b; border-radius: 4px; }
QLabel#sectionTitle { color: #a6e3a1; font-weight: bold; padding: 4px 2px; }
QLabel#preview { color: #a6e3a1; background-color: #11111b; padding: 6px 8px; border-radius: 4px; font-family: "Consolas", monospace; }
QLineEdit { background-color: #11111b; border: 1px solid #313244; border-radius: 4px; padding: 5px 8px; color: #cdd6f4; }
QLineEdit:focus { border: 1px solid #89b4fa; }
QTextEdit#output { background-color: #11111b; border: 1px solid #313244; border-radius: 6px; padding: 8px; color: #a6e3a1; font-family: "Consolas", monospace; }
QTabWidget::pane { border: 1px solid #313244; border-radius: 6px; background: #181825; }
QPushButton#tabButton { background-color: #181825; color: #bac2de; border: 1px solid #313244; border-radius: 4px; padding: 6px 14px; font-weight: normal; min-height: 22px; text-align: center; }
QPushButton#tabButton:hover { background-color: #45475a; color: #cdd6f4; }
QPushButton#tabButton:checked { background-color: #313244; color: #89b4fa; border: 1px solid #89b4fa; }
QPushButton#cmdBtn { background-color: #313244; color: #cdd6f4; border: 1px solid #45475a; border-radius: 4px; padding: 7px 10px; text-align: left; }
QPushButton#cmdBtn:hover { background-color: #45475a; border: 1px solid #89b4fa; }
QPushButton#cmdBtn:pressed { background-color: #585b70; }
QPushButton { background-color: #89b4fa; color: #11111b; border: none; border-radius: 4px; padding: 6px 14px; font-weight: bold; }
QPushButton:hover { background-color: #74a8f7; }
QPushButton:pressed { background-color: #5b93e6; }
QScrollArea { border: none; background: #181825; }
QScrollBar:vertical { background: #181825; width: 10px; margin: 0; }
QScrollBar::handle:vertical { background: #45475a; border-radius: 5px; min-height: 20px; }
QScrollBar::handle:vertical:hover { background: #585b70; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { background: #181825; height: 10px; margin: 0; }
QScrollBar::handle:horizontal { background: #45475a; border-radius: 5px; min-width: 20px; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
QGroupBox { border: 1px solid #313244; border-radius: 4px; margin-top: 10px; padding: 8px 6px 6px 6px; color: #bac2de; }
QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 4px; }
QCheckBox { color: #cdd6f4; padding: 2px; }
QCheckBox::indicator { width: 15px; height: 15px; }
QMessageBox, QDialog { background-color: #1e1e2e; }
QTextBrowser { background-color: #11111b; color: #cdd6f4; border: 1px solid #313244; border-radius: 6px; }
"""

LIGHT_STYLESHEET = """
QMainWindow, QWidget {
    background-color: #f5f5f5; color: #333333;
    font-family: "Consolas", "DejaVu Sans Mono", "Courier New", monospace; font-size: 13px;
}
QLabel#cwdLabel { color: #005a9e; font-weight: bold; padding: 4px 8px; background-color: #e0e0e0; border-radius: 4px; }
QLabel#sectionTitle { color: #2e7d32; font-weight: bold; padding: 4px 2px; }
QLabel#preview { color: #2e7d32; background-color: #e8f5e9; padding: 6px 8px; border-radius: 4px; border: 1px solid #c8e6c9; font-family: "Consolas", monospace; }
QLineEdit { background-color: #ffffff; border: 1px solid #cccccc; border-radius: 4px; padding: 5px 8px; color: #333333; }
QLineEdit:focus { border: 1px solid #005a9e; }
QTextEdit#output { background-color: #ffffff; border: 1px solid #cccccc; border-radius: 6px; padding: 8px; color: #1b5e20; font-family: "Consolas", monospace; }
QTabWidget::pane { border: 1px solid #cccccc; border-radius: 6px; background: #ffffff; }
QPushButton#tabButton { background-color: #ffffff; color: #555555; border: 1px solid #cccccc; border-radius: 4px; padding: 6px 14px; font-weight: normal; min-height: 22px; text-align: center; }
QPushButton#tabButton:hover { background-color: #eeeeee; color: #000000; }
QPushButton#tabButton:checked { background-color: #e3f2fd; color: #005a9e; border: 1px solid #005a9e; }
QPushButton#cmdBtn { background-color: #ffffff; color: #333333; border: 1px solid #cccccc; border-radius: 4px; padding: 7px 10px; text-align: left; }
QPushButton#cmdBtn:hover { background-color: #eeeeee; border: 1px solid #005a9e; }
QPushButton#cmdBtn:pressed { background-color: #dddddd; }
QPushButton { background-color: #005a9e; color: #ffffff; border: none; border-radius: 4px; padding: 6px 14px; font-weight: bold; }
QPushButton:hover { background-color: #004578; }
QPushButton:pressed { background-color: #003566; }
QScrollArea { border: none; background: #ffffff; }
QScrollBar:vertical { background: #f5f5f5; width: 10px; margin: 0; }
QScrollBar::handle:vertical { background: #cccccc; border-radius: 5px; min-height: 20px; }
QScrollBar::handle:vertical:hover { background: #aaaaaa; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { background: #f5f5f5; height: 10px; margin: 0; }
QScrollBar::handle:horizontal { background: #cccccc; border-radius: 5px; min-width: 20px; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
QGroupBox { border: 1px solid #cccccc; border-radius: 4px; margin-top: 10px; padding: 8px 6px 6px 6px; color: #555555; }
QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 4px; }
QCheckBox { color: #333333; padding: 2px; }
QCheckBox::indicator { width: 15px; height: 15px; }
QMessageBox, QDialog { background-color: #f5f5f5; }
QTextBrowser { background-color: #ffffff; color: #333333; border: 1px solid #cccccc; border-radius: 6px; }
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
            self._scroll_start = (self.horizontalScrollBar().value(), self.verticalScrollBar().value())
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
            if was_dragging: return True
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
        if self.buttons: self.buttons[0].setChecked(True)

    def _select(self, idx: int):
        for i, btn in enumerate(self.buttons):
            btn.setChecked(i == idx)
        self.category_selected.emit(idx)


# ---------------------------------------------------------------------- диалоги
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

    def get_command(self) -> str: return self.full_command


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


# ---------------------------------------------------------------- главное окно
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TEiL — Terminal Emulator in Linux")
        self.resize(1150, 720)
        
        self.is_light_theme = self.load_theme_setting()
        self.apply_theme()

        self.executor = CommandExecutor()
        self._build_ui()
        self._update_cwd()

        self._append_output(
            "Добро пожаловать в TEiL — эмулятор терминала Linux.\n"
            "Используйте строку поиска, чтобы быстро находить нужные команды.\n"
            "Настройки (тема и справочник) доступны в меню справа вверху.\n"
        )

    def load_theme_setting(self) -> bool:
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("is_light_theme", False)
            except Exception:
                return False
        return False

    def save_theme_setting(self):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump({"is_light_theme": self.is_light_theme}, f, indent=4)
        except Exception as e:
            print(f"Не удалось сохранить настройки: {e}")

    def apply_theme(self):
        app = QApplication.instance()
        if app:
            app.setStyleSheet(LIGHT_STYLESHEET if self.is_light_theme else DARK_STYLESHEET)

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
        
        btn_settings = QPushButton("⚙ Настройки")
        btn_settings.clicked.connect(self._open_settings)
        header.addWidget(btn_settings)
        
        root.addLayout(header)

        main_area = QHBoxLayout()
        left_panel = QWidget()
        left_panel.setMaximumWidth(380)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(6)

        # --- Поиск команд ---
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Поиск команд...")
        self.search_input.textChanged.connect(self._on_search)
        left_layout.addWidget(self.search_input)

        # --- Стек: Обычные вкладки или Результаты поиска ---
        self.stack = QStackedWidget()

        # Страница 0: Обычные вкладки
        tabs_page = QWidget()
        tabs_layout = QVBoxLayout(tabs_page)
        tabs_layout.setContentsMargins(0, 0, 0, 0)
        tabs_layout.setSpacing(6)

        self.category_bar = CategoryBar(list(CATEGORIES.keys()))
        tabs_layout.addWidget(self.category_bar)

        self.tabs = QTabWidget()
        self.tabs.tabBar().hide()
        self._build_tabs()
        tabs_layout.addWidget(self.tabs, 1)
        
        self.category_bar.category_selected.connect(self.tabs.setCurrentIndex)
        self.stack.addWidget(tabs_page)

        # Страница 1: Результаты поиска
        self.search_scroll = DragScrollArea()
        self.search_scroll.setWidgetResizable(True)
        self.search_container = QWidget()
        self.search_layout = QVBoxLayout(self.search_container)
        self.search_layout.setSpacing(6)
        self.search_layout.setContentsMargins(6, 6, 6, 6)
        self.search_scroll.setWidget(self.search_container)
        self.stack.addWidget(self.search_scroll)

        left_layout.addWidget(self.stack, 1)
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

    def _create_command_button(self, cmd: dict) -> QPushButton:
        btn = QPushButton(cmd["name"])
        btn.setToolTip(cmd.get("desc", ""))
        btn.setObjectName("cmdBtn")
        btn.clicked.connect(lambda _=False, c=cmd: self._on_command_clicked(c))
        return btn

    def _on_search(self, text: str):
        text = text.strip().lower()
        
        # Если поиск пуст, показываем обычные вкладки
        if not text:
            self.stack.setCurrentIndex(0)
            return

        self.stack.setCurrentIndex(1)

        # --- ИСПРАВЛЕНИЕ: Полная очистка layout ---
        while self.search_layout.count():
            item = self.search_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        # ------------------------------------------

        found = False
        for category, commands in CATEGORIES.items():
            for cmd in commands:
                name = cmd["name"].lower()
                desc = cmd.get("desc", "").lower()
                if text in name or text in desc:
                    btn = self._create_command_button(cmd)
                    self.search_layout.addWidget(btn)
                    found = True

        if not found:
            lbl = QLabel("Ничего не найдено")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.search_layout.addWidget(lbl)

        # Добавляем растяжку, чтобы кнопки прижимались к верху
        self.search_layout.addStretch()
        
        # Прокручиваем результат в самый верх
        self.search_scroll.verticalScrollBar().setValue(0)

    def _open_settings(self):
        dlg = SettingsDialog(self.is_light_theme, self)
        dlg.theme_changed.connect(self._change_theme)
        dlg.exec()

    def _change_theme(self, is_light: bool):
        self.is_light_theme = is_light
        self.apply_theme()
        self.save_theme_setting()

    def _build_tabs(self):
        for category, commands in CATEGORIES.items():
            scroll = DragScrollArea()
            scroll.setWidgetResizable(True)
            inner = QWidget()
            v = QVBoxLayout(inner)
            v.setSpacing(6)
            v.setContentsMargins(6, 6, 6, 6)
            for cmd in commands:
                btn = self._create_command_button(cmd)
                v.addWidget(btn)
            v.addStretch(1)
            scroll.setWidget(inner)
            self.tabs.addTab(scroll, category)

    def _on_command_clicked(self, cmd: dict):
        if cmd.get("instant"):
            self._execute(cmd["name"], cmd)
            return
        dlg = CommandDialog(cmd, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._execute(dlg.get_command(), cmd)

    def _execute(self, full_cmd: str, cmd: dict):
        self._append_output(f"\n$ {full_cmd}")
        handler = cmd.get("safe_handler")

        if handler == "touch":
            target = full_cmd[len("touch"):].strip()
            self._append_output(self.executor.safe_touch(target))
            return

        if handler == "mkdir":
            rest = full_cmd[len("mkdir"):].strip()
            parents = False
            target = rest
            if rest.startswith("-"):
                parts = rest.split(None, 1)
                if "p" in parts[0]: parents = True
                target = parts[1] if len(parts) > 1 else ""
            self._append_output(self.executor.safe_mkdir(target, parents))
            return

        if handler == "mv":
            rest = full_cmd[len("mv"):].strip()
            self._append_output(self.executor.safe_mv(rest))
            return

        if handler == "cp":
            rest = full_cmd[len("cp"):].strip()
            recursive = False
            if rest.startswith("-"):
                parts = rest.split(None, 1)
                if "r" in parts[0] or "R" in parts[0]: recursive = True
                rest = parts[1] if len(parts) > 1 else ""
            self._append_output(self.executor.safe_cp(rest, recursive))
            return

        if handler == "rm":
            target = full_cmd[len("rm"):].strip()
            ok, info = self.executor.describe_target(target)
            if not ok:
                self._append_output(f"rm: отказ — {info}")
                return

            reply = QMessageBox.warning(
                self, "TEiL — подтверждение удаления",
                f"Вы собираетесь удалить:\n\n{info}\n\nПродолжить?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                self._append_output("rm: отменено пользователем")
                return
            self._append_output(self.executor.safe_rm(target))
            return

        if cmd["name"] == "cd":
            target = full_cmd[len("cd"):].strip()
            if not target:
                self._append_output(self.executor.cwd)
            else:
                ok, err = self.executor.change_dir(target)
                if ok: self._update_cwd()
                else: self._append_output(err)
            return

        self._append_output(self.executor.execute(full_cmd))

    def _update_cwd(self):
        self.cwd_label.setText(self.executor.cwd)

    def _append_output(self, text: str):
        if not text.endswith("\n"): text += "\n"
        self.output.moveCursor(QTextCursor.MoveOperation.End)
        self.output.insertPlainText(text)
        self.output.moveCursor(QTextCursor.MoveOperation.End)