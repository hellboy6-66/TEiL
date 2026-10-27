import sys
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout

app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle("TEiL")
window.setFixedSize(1300, 700)

btn_file = QPushButton('Работа с файлами')
btn_viewing = QPushButton("Просмотр и редактирование содержимого файла")
btn_admin = QPushButton("Администрирование пользователей и прав")
btn_management = QPushButton("Управление процессами и системой")
btn_network = QPushButton("Сеть и подключение")
btn_package = QPushButton("Управление пакетами")
btn_archiving = QPushButton("Архивация и сжатие")

button_layout = QVBoxLayout()
button_layout.addWidget(btn_file)
button_layout.addWidget(btn_viewing)
button_layout.addWidget(btn_admin)
button_layout.addWidget(btn_management)
button_layout.addWidget(btn_network)
button_layout.addWidget(btn_package)
button_layout.addWidget(btn_archiving)

button_layout.addStretch()

main_layout = QHBoxLayout()
main_layout.addStretch()  
main_layout.addLayout(button_layout)

window.setLayout(main_layout)
window.show()

sys.exit(app.exec())