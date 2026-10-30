import sys
import os
import subprocess  
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QStackedLayout, QLabel, QInputDialog, QMessageBox
from PyQt6.QtCore import Qt
from functools import partial

app = QApplication(sys.argv)

# Запрещаем Qt закрывать приложение при закрытии диалоговых окон
app.setQuitOnLastWindowClosed(False)

window = QWidget()
window.setWindowTitle("TEiL")
window.setFixedSize(1300, 700)

# Принудительно завершаем процесс Python при закрытии главного окна на крестик
window.destroyed.connect(sys.exit)


# ================= ПЕРЕМЕННЫЕ ДЛЯ СТЕКА И ПРЕДЫДУЩЕЙ ПАПКИ =================
dir_stack = []
previous_working_dir = None  # Переменная для хранения предыдущей папки (для команды cd -)


# ================= ЛЕВАЯ ЧАСТЬ: ДИРЕКТОРИЯ =================
current_dir = os.getcwd()
dir_label = QLabel(f"Текущая директория:\n{current_dir}", parent=window)
dir_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

font = dir_label.font()
font.setPointSize(14)
font.setBold(True)
dir_label.setFont(font)

left_v_layout = QVBoxLayout()
left_v_layout.addStretch()
left_v_layout.addWidget(dir_label)
left_v_layout.addStretch()


# ================= ПРАВАЯ ЧАСТЬ: СЛОЕНЫЙ МАКЕТ =================
right_stacked_layout = QStackedLayout()

# --- ЭКРАН 1: Главное меню ---
menu_widget = QWidget(parent=window)
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
sub_widget = QWidget(parent=window)
sub_button_layout = QVBoxLayout()

btn_cd = QPushButton("cd (Смена директории)", parent=sub_widget)
btn_ls = QPushButton("ls (Список файлов)", parent=sub_widget)
btn_pushd = QPushButton("pushd (Поместить в стек и перейти)", parent=sub_widget)
btn_popd = QPushButton("popd (Извлечь из стека и вернуться)", parent=sub_widget)
btn_dirs = QPushButton("dirs (Показать стек директорий)", parent=sub_widget)
btn_cd_minus = QPushButton("cd - (Вернуться в прошлую папку)", parent=sub_widget)  # Наша новая кнопка
btn_back = QPushButton("Назад", parent=sub_widget)

# Добавляем все кнопки, включая cd -, в список для настройки размера
buttons_sub = [btn_cd, btn_ls, btn_pushd, btn_popd, btn_dirs, btn_cd_minus, btn_back]
for btn in buttons_sub:
    btn.setFixedWidth(350)
    sub_button_layout.addWidget(btn)

sub_button_layout.addStretch()

sub_menu_layout = QHBoxLayout()
sub_menu_layout.addStretch()
sub_menu_layout.addLayout(sub_button_layout)
sub_widget.setLayout(sub_menu_layout)


# Добавляем экраны в стек
right_stacked_layout.addWidget(menu_widget)  # Индекс 0
right_stacked_layout.addWidget(sub_widget)   # Индекс 1


# ================= ЛОГИКА И ОБРАБОТКА НАЖАТИЙ =================

def show_file_sub_screen():
    right_stacked_layout.setCurrentIndex(1) 

def show_main_screen():
    right_stacked_layout.setCurrentIndex(0)  

# Логика для кнопки CD
def handle_cd_click():
    global previous_working_dir
    text, ok = QInputDialog.getText(window, "Смена директории", "Введите новый путь к директории:")
    if ok and text.strip():
        path_to_check = text.strip()
        if os.path.isdir(path_to_check):
            # Сохраняем папку перед переходом
            previous_working_dir = os.getcwd()
            
            os.chdir(path_to_check)
            dir_label.setText(f"Текущая директория:\n{os.getcwd()}")
        else:
            QMessageBox.warning(window, "Ошибка", f"Директория не найдена:\n{path_to_check}")

# Логика для кнопки LS
def handle_ls_click():
    keys, ok = QInputDialog.getText(window, "Параметры ls", "Введите ключи терминала (например: -l, -a, -la) или оставьте пустым:")
    if ok:
        keys = keys.strip()
        command = ["ls"]
        if keys:
            command.extend(keys.split())
        try:
            result = subprocess.check_output(command, cwd=os.getcwd(), text=True, stderr=subprocess.STDOUT)
            if not result.strip():
                result = "(Директория пуста)"
            QMessageBox.information(window, f"Результат: ls {keys}", result)
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(window, "Ошибка терминала", f"Команда завершилась с ошибкой:\n{e.output}")
        except Exception as e:
            QMessageBox.critical(window, "Критическая ошибка", f"Не удалось выполнить команду:\n{str(e)}")

# Логика для кнопки PUSHD
def handle_pushd_click():
    global previous_working_dir
    text, ok = QInputDialog.getText(window, "Команда pushd", "Введите путь к новой директории для перехода:")
    if ok and text.strip():
        path_to_check = text.strip()
        if os.path.isdir(path_to_check):
            # Сохраняем папку перед переходом для cd - и для стека
            previous_working_dir = os.getcwd()
            dir_stack.append(os.getcwd())
            
            os.chdir(path_to_check)
            dir_label.setText(f"Текущая директория:\n{os.getcwd()}")
            
            current_stack_str = " -> ".join([os.getcwd()] + dir_stack[::-1])
            QMessageBox.information(window, "pushd", f"Директория добавлена в стек.\nТекущий стек:\n{current_stack_str}")
        else:
            QMessageBox.warning(window, "Ошибка pushd", f"Директория не найдена:\n{path_to_check}")

# Логика для кнопки POPD
def handle_popd_click():
    global previous_working_dir
    if dir_stack:
        # Сохраняем перед переходом обратно
        previous_working_dir = os.getcwd()
        
        previous_dir = dir_stack.pop()
        os.chdir(previous_dir)
        dir_label.setText(f"Текущая директория:\n{os.getcwd()}")
        
        QMessageBox.information(window, "popd", f"Вернулись назад в:\n{previous_dir}")
    else:
        QMessageBox.warning(window, "Ошибка popd", "Стек директорий пуст! (directory stack empty)")

# Логика для кнопки DIRS
def handle_dirs_click():
    if not dir_stack:
        QMessageBox.information(window, "dirs", f"Стек пуст. Текущая папка:\n{os.getcwd()}")
    else:
        stack_list = [os.getcwd()] + dir_stack[::-1]
        formatted_stack = "\n".join([f"[{i}] {path}" for i, path in enumerate(stack_list)])
        QMessageBox.information(window, "Стек директорий (dirs)", formatted_stack)

# Логика для кнопки CD -
def handle_cd_minus_click():
    global previous_working_dir
    # Если мы еще ни разу не меняли папку с момента запуска программы
    if previous_working_dir is None:
        QMessageBox.warning(window, "cd -", "Предыдущая директория отсутствует (OLDPWD не задан)")
    else:
        # Запоминаем текущую папку, чтобы она стала "предыдущей" для следующего нажатия cd -
        temp_current = os.getcwd()
        
        # Переходим в прошлую папку
        os.chdir(previous_working_dir)
        dir_label.setText(f"Текущая директория:\n{os.getcwd()}")
        
        # Выводим путь в окно, точно так же, как Linux выводит его в терминал
        QMessageBox.information(window, "cd -", f"Перешли в предыдущую директорию:\n{os.getcwd()}")
        
        # Обновляем историю переходов
        previous_working_dir = temp_current


# Привязка событий к главным кнопкам
btn_file.clicked.connect(show_file_sub_screen)
btn_viewing.clicked.connect(partial(QMessageBox.information, window, "Инфо", "Раздел в разработке"))
btn_admin.clicked.connect(partial(QMessageBox.information, window, "Инфо", "Раздел в разработке"))
btn_management.clicked.connect(partial(QMessageBox.information, window, "Инфо", "Раздел в разработке"))
btn_network.clicked.connect(partial(QMessageBox.information, window, "Инфо", "Раздел в разработке"))
btn_package.clicked.connect(partial(QMessageBox.information, window, "Инфо", "Раздел в разработке"))
btn_archiving.clicked.connect(partial(QMessageBox.information, window, "Инфо", "Раздел в разработке"))

# Привязка кнопок внутри подменю файлов
btn_cd.clicked.connect(handle_cd_click)
btn_ls.clicked.connect(handle_ls_click)
btn_pushd.clicked.connect(handle_pushd_click)
btn_popd.clicked.connect(handle_popd_click)
btn_dirs.clicked.connect(handle_dirs_click)
btn_cd_minus.clicked.connect(handle_cd_minus_click)  # Привязываем новую кнопку
btn_back.clicked.connect(show_main_screen)


# ================= СБОРКА И ЗАПУСК =================
main_layout = QHBoxLayout(window)
main_layout.addLayout(left_v_layout, stretch=1)
main_layout.addStretch()
main_layout.addLayout(right_stacked_layout)

window.show()
sys.exit(app.exec())
