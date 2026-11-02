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

        # Строго по списку с картинки
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
            btn.setFixedWidth(450) 
            btn.setStyleSheet("QPushButton { text-align: center; qproperty-wordWrap: true; padding: 10px; }")
            button_layout.addWidget(btn)
        button_layout.addStretch()

        menu_layout = QHBoxLayout()
        menu_layout.addStretch()
        menu_layout.addLayout(button_layout)
        menu_widget.setLayout(menu_layout)

        # --- ЭКРАН 2: Подменю "Навигация и работа с каталогами" (Индекс 1) ---
        sub_widget_nav = QWidget(parent=self)
        sub_button_layout_nav = QVBoxLayout()

        btn_cd = QPushButton("cd (Смена директории)", parent=sub_widget_nav)
        btn_ls = QPushButton("ls (Список файлов)", parent=sub_widget_nav)
        btn_pushd = QPushButton("pushd (Поместить в стек и перейти)", parent=sub_widget_nav)
        btn_popd = QPushButton("popd (Извлечь из стека и вернуться)", parent=sub_widget_nav)
        btn_dirs = QPushButton("dirs (Показать стек директорий)", parent=sub_widget_nav)
        btn_cd_minus = QPushButton("cd - (Вернуться в прошлую папку)", parent=sub_widget_nav)
        btn_back_nav = QPushButton("Назад", parent=sub_widget_nav)

        buttons_sub_nav = [btn_cd, btn_ls, btn_pushd, btn_popd, btn_dirs, btn_cd_minus, btn_back_nav]
        for btn in buttons_sub_nav:
            btn.setFixedWidth(450) 
            btn.setStyleSheet("QPushButton { text-align: center; qproperty-wordWrap: true; padding: 10px; }")
            sub_button_layout_nav.addWidget(btn)
        sub_button_layout_nav.addStretch()

        sub_menu_layout_nav = QHBoxLayout()
        sub_menu_layout_nav.addStretch()
        sub_menu_layout_nav.addLayout(sub_button_layout_nav)
        sub_widget_nav.setLayout(sub_menu_layout_nav)

        # --- ЭКРАН 3: Подменю "Управление файлами и папками" (Индекс 2) ---
        sub_widget_files = QWidget(parent=self)
        sub_button_layout_files = QVBoxLayout()

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
            btn.setFixedWidth(450)
            btn.setStyleSheet("QPushButton { text-align: center; qproperty-wordWrap: true; padding: 10px; }")
            sub_button_layout_files.addWidget(btn)
        sub_button_layout_files.addStretch()

        sub_menu_layout_files = QHBoxLayout()
        sub_menu_layout_files.addStretch()
        sub_menu_layout_files.addLayout(sub_button_layout_files)
        sub_widget_files.setLayout(sub_menu_layout_files)

        # Добавляем все три экрана в стек
        self.right_stacked_layout.addWidget(menu_widget)       # Индекс 0
        self.right_stacked_layout.addWidget(sub_widget_nav)    # Индекс 1
        self.right_stacked_layout.addWidget(sub_widget_files)  # Индекс 2

        # ================= ПРИВЯЗКА СОБЫТИЙ К КНОПКАМ =================
        btn_nav.clicked.connect(self.show_nav_sub_screen)
        btn_files.clicked.connect(self.show_files_sub_screen) 
        
        # Кнопки в разработке
        in_dev = partial(QMessageBox.information, self, "Инфо", "Раздел в разработке")
        btn_text.clicked.connect(in_dev)
        btn_perms.clicked.connect(in_dev)
        btn_proc.clicked.connect(in_dev)
        btn_sys.clicked.connect(in_dev)
        btn_users.clicked.connect(in_dev)
        btn_pkg.clicked.connect(in_dev)
        btn_net.clicked.connect(in_dev)
        btn_help.clicked.connect(in_dev)

        # Логика экрана "Навигация и работа с каталогами" (Экран 1)
        btn_cd.clicked.connect(partial(self.cmd_logic.handle_cd, self, self.update_directory_label))
        btn_ls.clicked.connect(partial(self.cmd_logic.handle_ls, self))
        btn_pushd.clicked.connect(partial(self.cmd_logic.handle_pushd, self, self.update_directory_label))
        btn_popd.clicked.connect(partial(self.cmd_logic.handle_popd, self, self.update_directory_label))
        btn_dirs.clicked.connect(partial(self.cmd_logic.handle_dirs, self))
        btn_cd_minus.clicked.connect(partial(self.cmd_logic.handle_cd_minus, self, self.update_directory_label))
        btn_back_nav.clicked.connect(self.show_main_screen)

        # Логика экрана "Управление файлами и папками" (Экран 2)
        btn_touch.clicked.connect(partial(self.cmd_logic.handle_touch, self)) 
        btn_mkdir.clicked.connect(partial(self.cmd_logic.handle_mkdir, self))
        btn_cp.clicked.connect(partial(self.cmd_logic.handle_cp, self))
        btn_mv.clicked.connect(partial(self.cmd_logic.handle_mv, self))
        btn_rm.clicked.connect(partial(self.cmd_logic.handle_rm, self))
        btn_find.clicked.connect(partial(self.cmd_logic.handle_find, self))
        btn_locate.clicked.connect(partial(self.cmd_logic.handle_locate, self))
        btn_back_files.clicked.connect(self.show_main_screen)

        # Финальная сборка главного окна
        main_layout = QHBoxLayout(self)
        main_layout.addLayout(left_v_layout, stretch=1)
        main_layout.addStretch()
        main_layout.addLayout(self.right_stacked_layout)

    def show_nav_sub_screen(self):
        self.right_stacked_layout.setCurrentIndex(1) 

    def show_files_sub_screen(self):
        self.right_stacked_layout.setCurrentIndex(2) 

    def show_main_screen(self):
        self.right_stacked_layout.setCurrentIndex(0)  

    def update_directory_label(self, new_path):
        self.dir_label.setText(f"Текущая директория:\n{new_path}")