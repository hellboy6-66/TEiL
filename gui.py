import os
from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QStackedLayout, QLabel, QMessageBox
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

        # ================= ЛЕВАЯ ЧАСТЬ: ВЫВОД ДИРЕКТОРИИ =================
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

        # ================= ПРАВАЯ ЧАСТЬ: МЕНЮ С ЭКРАНАМИ =================
        self.right_stacked_layout = QStackedLayout()

        # --- ЭКРАН 1: Главное меню (Индекс 0) ---
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
            btn.setFixedWidth(450) 
            btn.setStyleSheet("QPushButton { text-align: center; qproperty-wordWrap: true; }")
            button_layout.addWidget(btn)
        button_layout.addStretch()

        menu_layout = QHBoxLayout()
        menu_layout.addStretch()
        menu_layout.addLayout(button_layout)
        menu_widget.setLayout(menu_layout)

        # --- ЭКРАН 2: Подменю "Работа с файлами" (Индекс 1) ---
        sub_widget_file = QWidget(parent=self)
        sub_button_layout_file = QVBoxLayout()

        btn_cd = QPushButton("cd (Смена директории)", parent=sub_widget_file)
        btn_ls = QPushButton("ls (Список файлов)", parent=sub_widget_file)
        btn_pushd = QPushButton("pushd (Поместить в стек и перейти)", parent=sub_widget_file)
        btn_popd = QPushButton("popd (Извлечь из стека и вернуться)", parent=sub_widget_file)
        btn_dirs = QPushButton("dirs (Показать стек директорий)", parent=sub_widget_file)
        btn_cd_minus = QPushButton("cd - (Вернуться в прошлую папку)", parent=sub_widget_file)
        btn_find = QPushButton("find (Поиск файлов в текущей папке)", parent=sub_widget_file)
        btn_locate = QPushButton("locate (Быстрый поиск по системе)", parent=sub_widget_file)
        btn_back_file = QPushButton("Назад", parent=sub_widget_file)

        buttons_sub_file = [btn_cd, btn_ls, btn_pushd, btn_popd, btn_dirs, btn_cd_minus, btn_find, btn_locate, btn_back_file]
        for btn in buttons_sub_file:
            btn.setFixedWidth(450) 
            btn.setStyleSheet("QPushButton { text-align: center; qproperty-wordWrap: true; }")
            sub_button_layout_file.addWidget(btn)
        sub_button_layout_file.addStretch()

        sub_menu_layout_file = QHBoxLayout()
        sub_menu_layout_file.addStretch()
        sub_menu_layout_file.addLayout(sub_button_layout_file)
        sub_widget_file.setLayout(sub_menu_layout_file)

        # --- ЭКРАН 3: Подменю "Просмотр и редактирование" (Индекс 2) ---
        sub_widget_view = QWidget(parent=self)
        sub_button_layout_view = QVBoxLayout()

        # Добавляем сюда кнопку touch
        btn_touch = QPushButton("touch (Создать/обновить файл)", parent=sub_widget_view)
        btn_back_view = QPushButton("Назад", parent=sub_widget_view)

        buttons_sub_view = [btn_touch, btn_back_view]
        for btn in buttons_sub_view:
            btn.setFixedWidth(450)
            btn.setStyleSheet("QPushButton { text-align: center; qproperty-wordWrap: true; }")
            sub_button_layout_view.addWidget(btn)
        sub_button_layout_view.addStretch()

        sub_menu_layout_view = QHBoxLayout()
        sub_menu_layout_view.addStretch()
        sub_menu_layout_view.addLayout(sub_button_layout_view)
        sub_widget_view.setLayout(sub_menu_layout_view)

        # Добавляем все три экрана в стек
        self.right_stacked_layout.addWidget(menu_widget)       # Индекс 0
        self.right_stacked_layout.addWidget(sub_widget_file)  # Индекс 1
        self.right_stacked_layout.addWidget(sub_widget_view)  # Индекс 2

        # ================= ПРИВЯЗКА СОБЫТИЙ К КНОПКАМ =================
        # Переходы по экранам меню
        btn_file.clicked.connect(self.show_file_sub_screen)
        btn_viewing.clicked.connect(self.show_view_sub_screen) # Открывает экран 3
        
        # Заглушки для остальных меню
        in_dev = partial(QMessageBox.information, self, "Инфо", "Раздел в разработке")
        btn_admin.clicked.connect(in_dev)
        btn_management.clicked.connect(in_dev)
        btn_network.clicked.connect(in_dev)
        btn_package.clicked.connect(in_dev)
        btn_archiving.clicked.connect(in_dev)

        # Логика экрана "Работа с файлами" (Экран 2)
        btn_cd.clicked.connect(partial(self.cmd_logic.handle_cd, self, self.update_directory_label))
        btn_ls.clicked.connect(partial(self.cmd_logic.handle_ls, self))
        btn_pushd.clicked.connect(partial(self.cmd_logic.handle_pushd, self, self.update_directory_label))
        btn_popd.clicked.connect(partial(self.cmd_logic.handle_popd, self, self.update_directory_label))
        btn_dirs.clicked.connect(partial(self.cmd_logic.handle_dirs, self))
        btn_cd_minus.clicked.connect(partial(self.cmd_logic.handle_cd_minus, self, self.update_directory_label))
        btn_find.clicked.connect(partial(self.cmd_logic.handle_find, self))
        btn_locate.clicked.connect(partial(self.cmd_logic.handle_locate, self))
        btn_back_file.clicked.connect(self.show_main_screen)

        # Логика экрана "Просмотр и редактирование" (Экран 3)
        btn_touch.clicked.connect(partial(self.cmd_logic.handle_touch, self)) # Привязываем touch здесь
        btn_back_view.clicked.connect(self.show_main_screen)

        # Финальная сборка главного окна
        main_layout = QHBoxLayout(self)
        main_layout.addLayout(left_v_layout, stretch=1)
        main_layout.addStretch()
        main_layout.addLayout(self.right_stacked_layout)

    def show_file_sub_screen(self):
        self.right_stacked_layout.setCurrentIndex(1) 

    def show_view_sub_screen(self):
        self.right_stacked_layout.setCurrentIndex(2) 

    def show_main_screen(self):
        self.right_stacked_layout.setCurrentIndex(0)  

    def update_directory_label(self, new_path):
        self.dir_label.setText(f"Текущая директория:\n{new_path}")
