"""Главное окно приложения TEiL."""

import os
import shlex
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTabWidget, QTextEdit, 
    QMessageBox, QApplication, QStackedWidget, QDialog, QCompleter,
    QSplitter, QTreeView, QHeaderView
)
from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QTextCursor, QFileSystemModel

from commands import CATEGORIES, CommandExecutor
from styles import DARK_STYLESHEET, LIGHT_STYLESHEET
from widgets import DragScrollArea, CategoryBar
from dialogs import CommandDialog, SettingsDialog, LessonDialog
from workers import CommandWorker
import config

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TEiL — Terminal Emulator in Linux")
        self.resize(1400, 750)
        
        settings = config.load_settings()
        self.is_light_theme = settings["is_light_theme"]
        self.saved_history = settings["history"]
        self.max_history = settings["max_history"]
        self.lesson_idx = settings.get("lesson_idx", 0)
        
        self.apply_theme()

        self.executor = CommandExecutor(settings["cwd"])
        self.cmd_history = self.saved_history
        self.history_pos = len(self.cmd_history)
        self.worker = None
        self.last_executed_cmd = ""
        self.lesson_dlg = None
        
        self.all_cmd_names = []
        for cat_cmds in CATEGORIES.values():
            for cmd in cat_cmds:
                self.all_cmd_names.append(cmd["name"])

        self._build_ui()
        self._update_cwd()

        welcome_html = """
        <div style="font-family: 'Consolas', 'DejaVu Sans Mono', monospace;">
            <h1 style="margin-bottom: 0px; font-size: 28px;">TEiL</h1>
            <p style="margin-top: 0px; font-size: 14px;"><b>Terminal Emulator in Linux</b></p>
            <hr>
            <p>Добро пожаловать в TEiL!</p>
            <p><b>Как пользоваться:</b></p>
            <ul>
                <li> <b>Дерево файлов:</b> слева отображается текущая папка.</li>
                <li> <b>Ручной ввод:</b> введите команду в строке внизу и нажмите <i>Enter</i>.</li>
                <li> <b>Кнопки:</b> справа выберите команду, настройте флаги и нажмите «Выполнить».</li>
            </ul>
            <p><b> Полезные советы:</b></p>
            <ul>
                <li>Используйте <b>⬆ (Стрелка Вверх)</b> на клавиатуре для вызова истории.</li>
                <li>Откройте <b>⚙ Настройки</b>, чтобы сменить тему, прочитать справку или пройти <b>обучающие задания</b>.</li>
            </ul>
            <br>
        </div>
        """
        self.output.insertHtml(welcome_html)
        self.output.moveCursor(QTextCursor.MoveOperation.End)

    def save_config(self):
        config.save_settings(
            self.is_light_theme, 
            self.executor.cwd, 
            self.cmd_history, 
            self.max_history,
            self.lesson_idx
        )

    def closeEvent(self, event):
        self.save_config()
        super().closeEvent(event)

    def apply_theme(self):
        app = QApplication.instance()
        if app:
            app.setStyleSheet(LIGHT_STYLESHEET if self.is_light_theme else DARK_STYLESHEET)

    def eventFilter(self, obj, event):
        is_input = (obj == self.manual_input)
        is_popup = (self.manual_input.completer() and obj == self.manual_input.completer().popup())
        
        if is_input or is_popup:
            if event.type() == QEvent.Type.ShortcutOverride and event.key() == Qt.Key.Key_Tab:
                return True
                
            if event.type() == QEvent.Type.KeyPress:
                if event.key() == Qt.Key.Key_Up:
                    self._on_history_up()
                    return True
                elif event.key() == Qt.Key.Key_Down:
                    self._on_history_down()
                    return True
                elif event.key() == Qt.Key.Key_Tab:
                    text = self.manual_input.text().strip().lower()
                    if text:
                        for cmd_name in self.all_cmd_names:
                            if cmd_name.startswith(text):
                                self.manual_input.setText(cmd_name)
                                self.manual_input.setCursorPosition(len(cmd_name))
                                break
                    
                    if self.manual_input.completer():
                        self.manual_input.completer().popup().hide()
                    self.manual_input.setFocus()
                    return True
                    
        return super().eventFilter(obj, event)

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

        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        self.tree_view = QTreeView()
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath(self.executor.cwd)
        self.tree_view.setModel(self.file_model)
        
        self.tree_view.setRootIndex(self.file_model.index(self.executor.cwd))
        self.tree_view.setColumnHidden(1, True) 
        self.tree_view.setColumnHidden(2, True) 
        self.tree_view.setColumnHidden(3, True) 
        self.tree_view.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        
        self.main_splitter.addWidget(self.tree_view)

        terminal_panel = QWidget()
        term_layout = QVBoxLayout(terminal_panel)
        term_layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("Результат выполнения:")
        title.setObjectName("sectionTitle")
        term_layout.addWidget(title)

        self.output = QTextEdit()
        self.output.setObjectName("output")
        self.output.setReadOnly(True)
        term_layout.addWidget(self.output, 1)

        input_layout = QHBoxLayout()
        input_layout.setSpacing(4)

        self.manual_input = QLineEdit()
        self.manual_input.setPlaceholderText("Введите команду (например: ls -la) и нажмите Enter...")
        self.manual_input.returnPressed.connect(self._on_manual_input)
        self.manual_input.installEventFilter(self)

        completer = QCompleter(self.all_cmd_names, self)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion) 
        self.manual_input.setCompleter(completer)
        completer.popup().installEventFilter(self)

        self.btn_history_up = QPushButton("⬆")
        self.btn_history_up.setToolTip("Предыдущая команда из истории (Стрелка Вверх)")
        self.btn_history_up.setFixedSize(36, 28)
        self.btn_history_up.clicked.connect(self._on_history_up)

        input_layout.addWidget(self.manual_input)
        input_layout.addWidget(self.btn_history_up)
        term_layout.addLayout(input_layout)

        clear_btn = QPushButton("Очистить вывод")
        clear_btn.clicked.connect(self.output.clear)
        term_layout.addWidget(clear_btn)
        
        self.main_splitter.addWidget(terminal_panel)

        commands_panel = QWidget()
        commands_panel.setMinimumWidth(300)
        cmd_layout = QVBoxLayout(commands_panel)
        cmd_layout.setContentsMargins(0, 0, 0, 0)
        cmd_layout.setSpacing(6)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Поиск команд...")
        self.search_input.textChanged.connect(self._on_search)
        cmd_layout.addWidget(self.search_input)

        self.stack = QStackedWidget()

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

        self.search_scroll = DragScrollArea()
        self.search_scroll.setWidgetResizable(True)
        self.search_container = QWidget()
        self.search_layout = QVBoxLayout(self.search_container)
        self.search_layout.setSpacing(6)
        self.search_layout.setContentsMargins(6, 6, 6, 6)
        self.search_scroll.setWidget(self.search_container)
        self.stack.addWidget(self.search_scroll)

        cmd_layout.addWidget(self.stack, 1)
        self.main_splitter.addWidget(commands_panel)

        self.main_splitter.setSizes([250, 550, 350])
        self.main_splitter.setStretchFactor(0, 0)
        self.main_splitter.setStretchFactor(1, 1)
        self.main_splitter.setStretchFactor(2, 0)

        root.addWidget(self.main_splitter, 1)

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

    def _on_history_up(self):
        if not self.cmd_history: return
        self.history_pos -= 1
        if self.history_pos < 0: self.history_pos = len(self.cmd_history) - 1
        self.manual_input.setText(self.cmd_history[self.history_pos])
        self.manual_input.setCursorPosition(len(self.manual_input.text()))

    def _on_history_down(self):
        if not self.cmd_history: return
        self.history_pos += 1
        if self.history_pos >= len(self.cmd_history): self.history_pos = 0
        self.manual_input.setText(self.cmd_history[self.history_pos])
        self.manual_input.setCursorPosition(len(self.manual_input.text()))

    def _on_manual_input(self):
        text = self.manual_input.text().strip()
        if not text: return
        self.manual_input.clear()
        
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
        dlg = SettingsDialog(self.is_light_theme, self.max_history, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            is_light, limit = dlg.get_settings()
            
            self.is_light_theme = is_light
            self.apply_theme()
            
            self.max_history = limit
            if len(self.cmd_history) > self.max_history:
                self.cmd_history = self.cmd_history[-self.max_history:]
                self.history_pos = len(self.cmd_history)
                
            self.save_config()

    def _open_lessons(self):
        """Открывает окно уроков без блокировки главного окна (через show)"""
        if self.lesson_dlg is not None:
            self.lesson_dlg.close()
            
        self.lesson_dlg = LessonDialog(self.lesson_idx, self)
        self.lesson_dlg.progress_updated.connect(self._on_lesson_progress)
        self.lesson_dlg.finished.connect(self._on_lesson_closed)
        
        self.lesson_dlg.show()
        self.lesson_dlg.raise_()
        self.lesson_dlg.activateWindow()
        
        self.lesson_dlg.check_command(self.last_executed_cmd, self.executor.cwd)

    def _on_lesson_closed(self):
        self.lesson_dlg = None

    def _on_lesson_progress(self, new_idx: int):
        self.lesson_idx = new_idx
        self.save_config()

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

    def _run_in_thread(self, func, *args):
        self.manual_input.setEnabled(False)
        self.btn_history_up.setEnabled(False)
        self.search_input.setEnabled(False)
        self.stack.setEnabled(False)
        self._append_output("[выполняется...]")
        
        self.worker = CommandWorker(func, *args)
        self.worker.result_ready.connect(self._on_thread_finished)
        self.worker.start()

    def _on_thread_finished(self, result):
        self.manual_input.setEnabled(True)
        self.btn_history_up.setEnabled(True)
        self.search_input.setEnabled(True)
        self.stack.setEnabled(True)
        
        self._append_output(result)
        self._update_cwd()
        
        if self.lesson_dlg and self.lesson_dlg.isVisible():
            self.lesson_dlg.check_command(self.last_executed_cmd, self.executor.cwd)

    def _execute(self, full_cmd: str, cmd: dict):
        name = cmd["name"]
        self.last_executed_cmd = full_cmd

        if name == "clear":
            self.output.clear()
            return
        if name == "history":
            self._append_output("\n$ history")
            if not self.cmd_history:
                self._append_output("[история пуста]")
            else:
                for i, h_cmd in enumerate(self.cmd_history, 1):
                    self._append_output(f"{i:3d}  {h_cmd}")
            return

        if full_cmd not in ("clear", "history"):
            self.cmd_history.append(full_cmd)
            self.history_pos = len(self.cmd_history)
            
            if len(self.cmd_history) > self.max_history:
                self.cmd_history = self.cmd_history[-self.max_history:]
                self.history_pos = len(self.cmd_history)

        self._append_output(f"\n$ {full_cmd}")
        handler = cmd.get("safe_handler")

        if handler == "touch":
            target = full_cmd[len("touch"):].strip()
            self._run_in_thread(self.executor.safe_touch, target)
            return
        if handler == "mkdir":
            rest = full_cmd[len("mkdir"):].strip()
            parents = False
            if rest.startswith("-"):
                parts = rest.split(None, 1)
                if "p" in parts[0]: parents = True
                rest = parts[1] if len(parts) > 1 else ""
            self._run_in_thread(self.executor.safe_mkdir, rest, parents)
            return
        if handler == "mv":
            rest = full_cmd[len("mv"):].strip()
            self._run_in_thread(self.executor.safe_mv, rest)
            return
        if handler == "cp":
            rest = full_cmd[len("cp"):].strip()
            recursive = False
            if rest.startswith("-"):
                parts = rest.split(None, 1)
                if "r" in parts[0] or "R" in parts[0]: recursive = True
                rest = parts[1] if len(parts) > 1 else ""
            self._run_in_thread(self.executor.safe_cp, rest, recursive)
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
            self._run_in_thread(self.executor.safe_rm, target)
            return
        if name == "cd":
            target = full_cmd[len("cd"):].strip()
            if not target:
                self._append_output(self.executor.cwd)
            else:
                ok, err = self.executor.change_dir(target)
                if ok: 
                    self._update_cwd()
                    if self.lesson_dlg and self.lesson_dlg.isVisible():
                        self.lesson_dlg.check_command(self.last_executed_cmd, self.executor.cwd)
                else: self._append_output(err)
            return

        self._run_in_thread(self.executor.execute, full_cmd)

    def _update_cwd(self):
        self.cwd_label.setText(self.executor.cwd)
        self.tree_view.setRootIndex(self.file_model.index(self.executor.cwd))

    def _append_output(self, text: str):
        if not text.endswith("\n"): text += "\n"
        self.output.moveCursor(QTextCursor.MoveOperation.End)
        self.output.insertPlainText(text)
        self.output.moveCursor(QTextCursor.MoveOperation.End)