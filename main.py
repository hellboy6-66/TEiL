import sys
import os
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QStackedLayout, QLabel, QInputDialog, QMessageBox
from PyQt6.QtCore import Qt
from functools import partial

app = QApplication(sys.argv)
app.setQuitOnLastWindowClosed(False)
window = QWidget()
window.setWindowTitle("TEiL")
window.setFixedSize(1300, 700)

current_dir = os.getcwd()
dir_label = QLabel(f"Текущая директория:\n{current_dir}")
dir_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
font = dir_label.font()
font.setPointSize(14)
font.setBold(True)
dir_label.setFont(font)
left_v_layout = QVBoxLayout()
left_v_layout.addStretch()
left_v_layout.addWidget(dir_label)
left_v_layout.addStretch()

right_stacked_layout = QStackedLayout()

menu_widget = QWidget(parent=window)
button_layout = QVBoxLayout()

btn_file = QPushButton('Работа с файлами')
btn_viewing = QPushButton("Просмотр и редактирование содержимого файла")
btn_admin = QPushButton("Администрирование пользователей и прав")
btn_management = QPushButton("Управление процессами и системой")
btn_network = QPushButton("Сеть и подключение")
btn_package = QPushButton("Управление пакетами")
btn_archiving = QPushButton("Архивация и сжатие")

button_layout.addWidget(btn_file)
button_layout.addWidget(btn_viewing)
button_layout.addWidget(btn_admin)
button_layout.addWidget(btn_management)
button_layout.addWidget(btn_network)
button_layout.addWidget(btn_package)
button_layout.addWidget(btn_archiving)

button_layout.addStretch()

menu_layout = QHBoxLayout()
menu_layout.addStretch()
menu_layout.addLayout(button_layout)
menu_widget.setLayout(menu_layout)

sub_widget = QWidget(parent=window)
sub_layout = QVBoxLayout()

btn_number = QPushButton()
btn_back = QPushButton("Назад")

sub_button_layout = QVBoxLayout()
sub_button_layout.addWidget(btn_number)
sub_button_layout.addWidget(btn_back)
sub_button_layout.addStretch()

sub_menu_layout = QHBoxLayout()
sub_menu_layout.addStretch()
sub_menu_layout.addLayout(sub_button_layout)
sub_widget.setLayout(sub_menu_layout)

def show_sub_screen(button_number):
    btn_number.setText(f"{button_number}") 
    right_stacked_layout.setCurrentIndex(1) 

def show_main_screen():
    right_stacked_layout.setCurrentIndex(0)  

def handle_number_button_click():
    # Если на экране отображается именно Кнопка №1
    if btn_number.text() == 'cd':
        # Открываем всплывающее окно ввода текста
        text, ok = QInputDialog.getText(
            window, 
            "Смена директории", 
            "Введите новый путь к директории:"
        )
        if ok and text.strip():
            path_to_check = text.strip()
            if os.path.isdir(path_to_check):
                dir_label.setText(f"Текущая директория: \n{path_to_check}")
            else:
                QMessageBox.warning(
                    window, 
                    "Ошибка", 
                    f"Директория не найдена:\n{path_to_check}\n\nПожалуйста, введите корректный путь."
                )

btn_file.clicked.connect(partial( show_sub_screen, 'cd'))
btn_viewing.clicked.connect(partial( show_sub_screen, 2))
btn_admin.clicked.connect(partial( show_sub_screen, 3))
btn_management.clicked.connect(partial( show_sub_screen, 4))
btn_network.clicked.connect(partial( show_sub_screen, 5))
btn_package.clicked.connect(partial( show_sub_screen, 6))
btn_archiving.clicked.connect(partial( show_sub_screen, 7))

btn_back.clicked.connect(show_main_screen)
btn_number.clicked.connect(handle_number_button_click)

right_stacked_layout.addWidget(menu_widget) 
right_stacked_layout.addWidget(sub_widget) 

main_layout = QHBoxLayout()

main_layout.addLayout(left_v_layout, stretch=1)
main_layout.addStretch()
main_layout.addLayout(right_stacked_layout)

window.setLayout(main_layout)
window.show()

sys.exit(app.exec())