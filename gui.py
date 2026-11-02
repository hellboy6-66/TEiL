import os
from PyQt6.QtWidgets import (QWidget, QPushButton, QVBoxLayout, QHBoxLayout, 
                             QStackedLayout, QLabel, QMessageBox, QPlainTextEdit)
from PyQt6.QtCore import Qt
from functools import partial
from commands import TerminalCommands 

class MainAppWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.cmd_logic = TerminalCommands() 
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("TEiL")
        self.setFixedSize(1300, 700)

        # ================= ЛЕВАЯ ЧАСТЬ: ЗАГОЛОВОК И БЕЛАЯ ПАНЕЛЬ =================
        current_dir = os.getcwd()
        
        self.dir_label = QLabel(f"Текущая директория: {current_dir}", parent=self)
        self.dir_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.dir_label.setWordWrap(False)
        
        font = self.dir_label.font()
        font.setPointSize(12)
        font.setBold(True)
        self.dir_label.setFont(font)
        self.dir_label.setStyleSheet("padding-left: 5px;")

        self.output_console = QPlainTextEdit(parent=self)
        self.output_console.setReadOnly(True)
        self.output_console.setStyleSheet("""
            QPlainTextEdit {
                background-color: white;
                color: black;
                font-family: 'Courier New', Consolas, monospace;
                font-size: 14px;
                border: 1px solid #ccc;
                padding: 5px;
            }
        """)

        left_layout = QVBoxLayout()
        left_layout.addWidget(self.dir_label)
        left_layout.addWidget(self.output_console)

        # ================= ПРАВАЯ ЧАСТЬ: КОЛОНКА КНОПОК =================
        self.right_stacked_layout = QStackedLayout()

        # --- ЭКРАН 0: Главное меню ---
        menu_widget = QWidget(parent=self)
        button_layout = QVBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0) 

        btn_nav = QPushButton("Навигация и работа с каталогами", parent=menu_widget)
        btn_files = QPushButton("Управление файлами и папками", parent=menu_widget)
        btn_text = QPushButton("Просмотр и редактирование текста", parent=menu_widget)
        btn_perms = QPushButton("Права доступа и владельцы", parent=menu_widget)
        btn_proc = QPushButton("Управление процессами", parent=menu_widget)
        btn_sys = QPushButton("Системная информация и оборудование", parent=menu_widget)
        btn_users = QPushButton("Управление пользователями и группами", parent=menu_widget)
        btn_pkg = QPushButton("Управление пакетами (ПО)", parent=menu_widget)
        btn_net = QPushButton("Сеть и интернет", parent=menu_widget)
        btn_help = QPushButton("Справочные команды", parent=menu_widget)

        buttons_main = [btn_nav, btn_files, btn_text, btn_perms, btn_proc, btn_sys, btn_users, btn_pkg, btn_net, btn_help]
        for btn in buttons_main:
            btn.setFixedWidth(350) 
            btn.setStyleSheet("QPushButton { text-align: center; qproperty-wordWrap: true; padding: 8px; }")
            button_layout.addWidget(btn)
        button_layout.addStretch()

        menu_layout = QHBoxLayout()
        menu_layout.setContentsMargins(0, 0, 0, 0)
        menu_layout.addLayout(button_layout)
        menu_widget.setLayout(menu_layout)

        # --- ЭКРАН 1: Подменю "Навигация и работа с каталогами" ---
        sub_widget_nav = QWidget(parent=self)
        sub_button_layout_nav = QVBoxLayout()
        sub_button_layout_nav.setContentsMargins(0, 0, 0, 0)
        
        btn_cd = QPushButton("cd (Смена директории)", parent=sub_widget_nav)
        btn_ls = QPushButton("ls (Список файлов)", parent=sub_widget_nav)
        btn_pushd = QPushButton("pushd (Поместить в стек и перейти)", parent=sub_widget_nav)
        btn_popd = QPushButton("popd (Извлечь из стека и вернуться)", parent=sub_widget_nav)
        btn_dirs = QPushButton("dirs (Показать стек директорий)", parent=sub_widget_nav)
        btn_cd_minus = QPushButton("cd - (Вернуться в прошлую папку)", parent=sub_widget_nav)
        btn_back_nav = QPushButton("Назад", parent=sub_widget_nav)
        
        buttons_sub_nav = [btn_cd, btn_ls, btn_pushd, btn_popd, btn_dirs, btn_cd_minus, btn_back_nav]
        for btn in buttons_sub_nav:
            btn.setFixedWidth(350) 
            btn.setStyleSheet("QPushButton { text-align: center; padding: 8px; }")
            sub_button_layout_nav.addWidget(btn)
        sub_button_layout_nav.addStretch()
        
        sub_menu_layout_nav = QHBoxLayout()
        sub_menu_layout_nav.setContentsMargins(0, 0, 0, 0)
        sub_menu_layout_nav.addLayout(sub_button_layout_nav)
        sub_widget_nav.setLayout(sub_menu_layout_nav)

        # --- ЭКРАН 2: Подменю "Управление файлами и папками" ---
        sub_widget_files = QWidget(parent=self)
        sub_button_layout_files = QVBoxLayout()
        sub_button_layout_files.setContentsMargins(0, 0, 0, 0)
        
        btn_touch = QPushButton("touch (Создать/обновить файл)", parent=sub_widget_files)
        btn_mkdir = QPushButton("mkdir (Создать директорию)", parent=sub_widget_files)
        btn_cp = QPushButton("cp (Копировать файл/директорию)", parent=sub_widget_files)
        btn_mv = QPushButton("mv (Переместить/переименовать)", parent=sub_widget_files)
        btn_rm = QPushButton("rm (Удалить файл/директорию)", parent=sub_widget_files)
        btn_find = QPushButton("find (Поиск файлов в текущей папке)", parent=sub_widget_files)
        btn_locate = QPushButton("locate (Быстрый поиск по системе)", parent=sub_widget_files)
        btn_back_files = QPushButton("Назад", parent=sub_widget_files)
        
        buttons_sub_files = [btn_touch, btn_mkdir, btn_cp, btn_mv, btn_rm, btn_find, btn_locate, btn_back_files]
        for btn in buttons_sub_files:
            btn.setFixedWidth(350)
            btn.setStyleSheet("QPushButton { text-align: center; padding: 8px; }")
            sub_button_layout_files.addWidget(btn)
        sub_button_layout_files.addStretch()
        
        sub_menu_layout_files = QHBoxLayout()
        sub_menu_layout_files.setContentsMargins(0, 0, 0, 0)
        sub_menu_layout_files.addLayout(sub_button_layout_files)
        sub_widget_files.setLayout(sub_menu_layout_files)

        # --- ЭКРАН 3: Подменю "Просмотр и редактирование текста" ---
        sub_widget_text = QWidget(parent=self)
        sub_button_layout_text = QVBoxLayout()
        sub_button_layout_text.setContentsMargins(0, 0, 0, 0)
        
        btn_cat = QPushButton("cat (Вывод содержимого файла)", parent=sub_widget_text)
        btn_less = QPushButton("less (Постраничный просмотр)", parent=sub_widget_text)
        btn_head = QPushButton("head (Вывод первых N строк)", parent=sub_widget_text) # Новая кнопка
        btn_back_text = QPushButton("Назад", parent=sub_widget_text)
        
        buttons_sub_text = [btn_cat, btn_less, btn_head, btn_back_text] # Добавили btn_head
        for btn in buttons_sub_text:
            btn.setFixedWidth(350)
            btn.setStyleSheet("QPushButton { text-align: center; padding: 8px; }")
            sub_button_layout_text.addWidget(btn)
        sub_button_layout_text.addStretch()
        
        sub_menu_layout_text = QHBoxLayout()
        sub_menu_layout_text.setContentsMargins(0, 0, 0, 0)
        sub_menu_layout_text.addLayout(sub_button_layout_text)
        sub_widget_text.setLayout(sub_menu_layout_text)

        # Добавляем экраны в стек
        self.right_stacked_layout.addWidget(menu_widget)       # Индекс 0
        self.right_stacked_layout.addWidget(sub_widget_nav)    # Индекс 1
        self.right_stacked_layout.addWidget(sub_widget_files)  # Индекс 2
        self.right_stacked_layout.addWidget(sub_widget_text)   # Индекс 3

        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.addLayout(self.right_stacked_layout)

        # ================= ПРИВЯЗКА СОБЫТИЙ =================
        btn_nav.clicked.connect(self.show_nav_sub_screen)
        btn_files.clicked.connect(self.show_files_sub_screen) 
        btn_text.clicked.connect(self.show_text_sub_screen)
        
        in_dev = partial(QMessageBox.information, self, "Инфо", "Раздел в разработке")
        btn_perms.clicked.connect(in_dev)
        btn_proc.clicked.connect(in_dev)
        btn_sys.clicked.connect(in_dev)
        btn_users.clicked.connect(in_dev)
        btn_pkg.clicked.connect(in_dev)
        btn_net.clicked.connect(in_dev)
        btn_help.clicked.connect(in_dev)

        # --- Навигация ---
        btn_cd.clicked.connect(lambda: self.run_command("cd", self.cmd_logic.handle_cd, self, self.update_directory_label, self.print_to_console))
        btn_ls.clicked.connect(lambda: self.run_command("ls", self.cmd_logic.handle_ls, self, self.print_to_console))
        btn_pushd.clicked.connect(lambda: self.run_command("pushd", self.cmd_logic.handle_pushd, self, self.update_directory_label, self.print_to_console))
        btn_popd.clicked.connect(lambda: self.run_command("popd", self.cmd_logic.handle_popd, self, self.update_directory_label, self.print_to_console))
        btn_dirs.clicked.connect(lambda: self.run_command("dirs", self.cmd_logic.handle_dirs, self, self.print_to_console))
        btn_cd_minus.clicked.connect(lambda: self.run_command("cd -", self.cmd_logic.handle_cd_minus, self, self.update_directory_label, self.print_to_console))
        btn_back_nav.clicked.connect(self.show_main_screen)

        # --- Файлы ---
        btn_touch.clicked.connect(lambda: self.run_command("touch", self.cmd_logic.handle_touch, self, self.print_to_console))
        btn_mkdir.clicked.connect(lambda: self.run_command("mkdir", self.cmd_logic.handle_mkdir, self, self.print_to_console))
        btn_cp.clicked.connect(lambda: self.run_command("cp", self.cmd_logic.handle_cp, self, self.print_to_console))
        btn_mv.clicked.connect(lambda: self.run_command("mv", self.cmd_logic.handle_mv, self, self.print_to_console))
        btn_rm.clicked.connect(lambda: self.run_command("rm", self.cmd_logic.handle_rm, self, self.print_to_console))
        btn_find.clicked.connect(lambda: self.run_command("find", self.cmd_logic.handle_find, self, self.print_to_console))
        btn_locate.clicked.connect(lambda: self.run_command("locate", self.cmd_logic.handle_locate, self, self.print_to_console))
        btn_back_files.clicked.connect(self.show_main_screen)

        # --- Текст ---
        btn_cat.clicked.connect(lambda: self.run_command("cat", self.cmd_logic.handle_cat, self, self.print_to_console))
        btn_less.clicked.connect(lambda: self.run_command("less", self.cmd_logic.handle_less, self, self.print_to_console))
        btn_head.clicked.connect(lambda: self.run_command("head", self.cmd_logic.handle_head, self, self.print_to_console)) # Привязка head
        btn_back_text.clicked.connect(self.show_main_screen)

        # ================= ФИНАЛЬНАЯ СБОРКА ОКНА =================
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(20)
        
        main_layout.addLayout(left_layout, stretch=7)
        main_layout.addLayout(right_layout, stretch=3)

        # Приветствие при запуске
        self.print_to_console("Добро пожаловать в TEiL (Terminal Emulator in Linux).")
        self.print_to_console("Для начала работы выберите раздел справа.\n")

    def print_to_console(self, text):
        self.output_console.appendPlainText(text)
        self.output_console.ensureCursorVisible()

    def run_command(self, cmd_name, command_func, *args):
        self.print_to_console(f"\nteil@linux:~$ {cmd_name}")
        command_func(*args)

    def show_nav_sub_screen(self):
        self.right_stacked_layout.setCurrentIndex(1) 

    def show_files_sub_screen(self):
        self.right_stacked_layout.setCurrentIndex(2) 

    def show_text_sub_screen(self):
        self.right_stacked_layout.setCurrentIndex(3)

    def show_main_screen(self):
        self.right_stacked_layout.setCurrentIndex(0)  

    def update_directory_label(self, new_path):
        self.dir_label.setText(f"Текущая директория: {new_path}")