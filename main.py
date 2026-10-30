import sys
import os
import subprocess  # Импортируем модуль для запуска консольных команд Linux
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

# Теперь у нас тут фиксированные кнопки команд и кнопка Назад
btn_cd = QPushButton("cd (Смена директории)", parent=sub_widget)
btn_ls = QPushButton("ls (Список файлов)", parent=sub_widget)
btn_back = QPushButton("Назад", parent=sub_widget)

buttons_sub = [btn_cd, btn_ls, btn_back]
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

# Переход на экран подменю ("Работа с файлами")
def show_file_sub_screen():
    right_stacked_layout.setCurrentIndex(1) 

def show_main_screen():
    right_stacked_layout.setCurrentIndex(0)  

# Логика для кнопки CD
def handle_cd_click():
    text, ok = QInputDialog.getText(
        window, 
        "Смена директории", 
        "Введите новый путь к директории:"
    )
    if ok and text.strip():
        path_to_check = text.strip()
        if os.path.isdir(path_to_check):
            # Меняем текущую директорию в самом процессе Python, чтобы ls работал в ней!
            os.chdir(path_to_check)
            # Обновляем текст на экране
            dir_label.setText(f"Текущая директория:\n{os.getcwd()}")
        else:
            QMessageBox.warning(
                window, 
                "Ошибка", 
                f"Директория не найдена:\n{path_to_check}\n\nПожалуйста, введите корректный путь."
            )

# Логика для кнопки LS (Выполнение команды Linux)
def handle_ls_click():
    # Запрашиваем ключи у пользователя
    keys, ok = QInputDialog.getText(
        window, 
        "Параметры ls", 
        "Введите ключи терминала (например: -l, -a, -la) или оставьте пустым:"
    )
    
    # Если пользователь нажал OK (даже если строка пустая, это валидно для простого ls)
    if ok:
        keys = keys.strip()
        
        # Формируем команду. Если ввели ключи, добавляем их.
        command = ["ls"]
        if keys:
            # Разделяем строку ключей на отдельные аргументы (например, "-l -a" -> ["-l", "-a"])
            command.extend(keys.split())
            
        try:
            # Выполняем команду строго в текущей выбранной директории (cwd=os.getcwd())
            # text=True декодирует вывод из байтов в обычную строку текста
            result = subprocess.check_output(command, cwd=os.getcwd(), text=True, stderr=subprocess.STDOUT)
            
            # Если папка пустая, check_output вернет пустую строку
            if not result.strip():
                result = "(Директория пуста)"
                
            # Показываем результат выполнения команды пользователю
            QMessageBox.information(window, f"Результат: ls {keys}", result)
            
        except subprocess.CalledProcessError as e:
            # Если пользователь ввел неправильный ключ (например, -xyz которого нет в ls)
            QMessageBox.critical(window, "Ошибка терминала", f"Команда завершилась с ошибкой:\n{e.output}")
        except Exception as e:
            QMessageBox.critical(window, "Критическая ошибка", f"Не удалось выполнить команду:\n{str(e)}")


# Привязка событий к кнопкам
btn_file.clicked.connect(show_file_sub_screen)  # Теперь просто открывает подменю файлов

# Остальные кнопки пока просто ведут на заглушки (можно доработать позже)
btn_viewing.clicked.connect(partial(QMessageBox.information, window, "Инфо", "Раздел в разработке"))
btn_admin.clicked.connect(partial(QMessageBox.information, window, "Инфо", "Раздел в разработке"))
btn_management.clicked.connect(partial(QMessageBox.information, window, "Инфо", "Раздел в разработке"))
btn_network.clicked.connect(partial(QMessageBox.information, window, "Инфо", "Раздел в разработке"))
btn_package.clicked.connect(partial(QMessageBox.information, window, "Инфо", "Раздел в разработке"))
btn_archiving.clicked.connect(partial(QMessageBox.information, window, "Инфо", "Раздел в разработке"))

# Привязка кнопок внутри подменю файлов
btn_cd.clicked.connect(handle_cd_click)
btn_ls.clicked.connect(handle_ls_click)
btn_back.clicked.connect(show_main_screen)


# ================= СБОРКА И ЗАПУСК =================
main_layout = QHBoxLayout(window)
main_layout.addLayout(left_v_layout, stretch=1)
main_layout.addStretch()
main_layout.addLayout(right_stacked_layout)

window.show()
sys.exit(app.exec())
