"""Главное окно приложения TEiL."""

import os
import json
import shlex
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTabWidget, QTextEdit, 
    QMessageBox, QApplication, QStackedWidget, QDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextCursor

from commands import CATEGORIES, CommandExecutor
from styles import DARK_STYLESHEET, LIGHT_STYLESHEET
from widgets import DragScrollArea, CategoryBar
from dialogs import CommandDialog, SettingsDialog

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "teili_config.json")


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
            "Вы можете нажимать кнопки слева или вводить команды вручную\n"
            "в строке внизу (доступны только команды из меню).\n"
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

        # Шапка
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
        
        # Левая панель
        left_panel = QWidget()
        left_panel.setMaximumWidth(380)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(6)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Поиск команд...")
        self.search_input.textChanged.connect(self._on_search)
        left_layout.addWidget(self.search_input)

        self.stack = QStackedWidget()

        # Страница 0: Вкладки
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

        # Страница 1: Поиск
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

        # Правая панель
        right = QVBoxLayout()
        title = QLabel("Результат выполнения:")
        title.setObjectName("sectionTitle")
        right.addWidget(title)

        self.output = QTextEdit()
        self.output.setObjectName("output")
        self.output.setReadOnly(True)
        right.addWidget(self.output, 1)

        self.manual_input = QLineEdit()
        self.manual_input.setPlaceholderText("Введите команду (например: ls -la) и нажмите Enter...")
        self.manual_input.returnPressed.connect(self._on_manual_input)
        right.addWidget(self.manual_input)

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
        if not text:
            self.stack.setCurrentIndex(0)
            return

        self.stack.setCurrentIndex(1)

        while self.search_layout.count():
            item = self.search_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

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

        self.search_layout.addStretch()
        self.search_scroll.verticalScrollBar().setValue(0)

    def _on_manual_input(self):
        text = self.manual_input.text().strip()
        if not text: return
        self.manual_input.clear()
        
        # Правильно парсим базовую команду (даже если есть кавычки)
        try:
            parts = shlex.split(text)
        except ValueError:
            parts = text.split()
            
        base_name = parts[0] if parts else ""
        
        found_cmd = None
        for category, commands in CATEGORIES.items():
            for cmd in commands:
                if cmd["name"] == base_name:
                    found_cmd = cmd
                    break
            if found_cmd: break

        if found_cmd:
            self._execute(text, found_cmd)
        else:
            self._append_output(f"\n$ {text}")
            self._append_output(f"bash: {base_name}: команда не найдена\n"
                                f"(в TEiL ручной ввод доступен только для команд из меню)")

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
            if rest.startswith("-"):
                parts = rest.split(None, 1)
                if "p" in parts[0]: parents = True
                rest = parts[1] if len(parts) > 1 else ""
            self._append_output(self.executor.safe_mkdir(rest, parents))
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