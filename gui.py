import os
from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QStackedLayout, QLabel, QMessageBox
from PyQt6.QtCore import Qt
from functools import partial
from commands import TerminalCommands  # Импортируем нашу логику

class MainAppWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.cmd_logic = TerminalCommands()  # Подключаем контроллер команд
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("TEiL")
        self.setFixedSize(1300, 700)

        # ================= ЛЕВАЯ ЧАСТЬ =================
        current_dir = os.getcwd()
        self.dir_label = QLabel(f"Текущая директория:\n{current_dir}", parent=self)
        self.dir_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        font = self.dir_label.font()
        font.setPointSize(14)
        font.setBold(True)
        self.dir_label.setFont(font)

        left_v_layout = QVBoxLayout()
        left_v_layout.addStretch()
        left_v_layout.addWidget(self.dir_label)
        left_v_layout.addStretch()

        # ================= ПРАВАЯ ЧАСТЬ =================
        self.right_stacked_layout = QStackedLayout()

        # --- ЭКРАН 1: Главное меню ---
        menu_widget = QWidget(parent=self)
        button_layout = QVBoxLayout()

        btn_file = QPushButton('Работа с файлами', parent=menu_widget)
        btn_viewing = QPushButton("Просмотр и редактирование содержимого файла", parent=menu_widget)
        btn_admin = QPushButton("Адменистрирование пользователей и прав", parent=menu_widget)
        btn_management = QPushButton("Управление процессами и системой", parent=menu_widget)
        btn_network = QPushButton("Сеть и подключение", parent=menu_widget)
        btn_package = QPushButton("Управление пакетами", parent=menu_widget)
        btn_archiving = QPushButton("Архивация и сжатие", parent=menu_widget)

        buttons_main = [btn_file, btn_viewing, btn_admin, btn_management, btn_network, btn_package, btn_archiving]
        for btn in buttons_main:
            btn.setFixedWidth(350)
            button_layout.addWidget(btn)
        button_layout.addStretch()

        menu_layout = QHBoxLayout()
        menu_layout.addStretch()
        menu_layout.addLayout(button_layout)
        menu_widget.setLayout(menu_layout)

        # --- ЭКРАН 2: Подменю (Работа с файлами) ---
        sub_widget = QWidget(parent=self)
        sub_button_layout = QVBoxLayout()

        btn_cd = QPushButton("cd (Смена директории)", parent=sub_widget)
        btn_ls = QPushButton("ls (Список файлов)", parent=sub_widget)
        btn_pushd = QPushButton("pushd (Поместить в стек и перейти)", parent=sub_widget)
        btn_popd = QPushButton("popd (Извлечь из стека и вернуться)", parent=sub_widget)
        btn_dirs = QPushButton("dirs (Показать стек директорий)", parent=sub_widget)
        btn_cd_minus = QPushButton("cd - (Вернуться в прошлую папку)", parent=sub_widget)
        btn_find = QPushButton("find (Поиск файлов в текущей папке)", parent=sub_widget)
        btn_locate = QPushButton("locate (Быстрый поиск по системе)", parent=sub_widget)
        btn_back = QPushButton("Назад", parent=sub_widget)

        buttons_sub = [btn_cd, btn_ls, btn_pushd, btn_popd, btn_dirs, btn_cd_minus, btn_find, btn_locate, btn_back]
        for btn in buttons_sub:
            btn.setFixedWidth(350)
            sub_button_layout.addWidget(btn)
        sub_button_layout.addStretch()

        sub_menu_layout = QHBoxLayout()
        sub_menu_layout.addStretch()
        sub_menu_layout.addLayout(sub_button_layout)
        sub_widget.setLayout(sub_menu_layout)

        self.right_stacked_layout.addWidget(menu_widget)  
        self.right_stacked_layout.addWidget(sub_widget)   

        # ================= ПРИВЯЗКА СОБЫТИЙ =================
        btn_file.clicked.connect(self.show_file_sub_screen)
        
        # Заглушки для остальных меню
        in_dev = partial(QMessageBox.information, self, "Инфо", "Раздел в разработке")
        btn_viewing.clicked.connect(in_dev)
        btn_admin.clicked.connect(in_dev)
        btn_management.clicked.connect(in_dev)
        btn_network.clicked.connect(in_dev)
        btn_package.clicked.connect(in_dev)
        btn_archiving.clicked.connect(in_dev)

        # Вызовы логики из commands.py (передаем self как окно-родитель и метод обновления текста)
        btn_cd.clicked.connect(partial(self.cmd_logic.handle_cd, self, self.update_directory_label))
        btn_ls.clicked.connect(partial(self.cmd_logic.handle_ls, self))
        btn_pushd.clicked.connect(partial(self.cmd_logic.handle_pushd, self, self.update_directory_label))
        btn_popd.clicked.connect(partial(self.cmd_logic.handle_popd, self, self.update_directory_label))
        btn_dirs.clicked.connect(partial(self.cmd_logic.handle_dirs, self))
        btn_cd_minus.clicked.connect(partial(self.cmd_logic.handle_cd_minus, self, self.update_directory_label))
        btn_find.clicked.connect(partial(self.cmd_logic.handle_find, self))
        btn_locate.clicked.connect(partial(self.cmd_logic.handle_locate, self))
        
        btn_back.clicked.connect(self.show_main_screen)

        # Общая сборка макета окна
        main_layout = QHBoxLayout(self)
        main_layout.addLayout(left_v_layout, stretch=1)
        main_layout.addStretch()
        main_layout.addLayout(self.right_stacked_layout)

    def show_file_sub_screen(self):
        self.right_stacked_layout.setCurrentIndex(1) 

    def show_main_screen(self):
        self.right_stacked_layout.setCurrentIndex(0)  

    def update_directory_label(self, new_path):
        """Этот метод передается бэкенду, чтобы он мог обновлять текст на экране"""
        self.dir_label.setText(f"Текущая директория:\n{new_path}")
