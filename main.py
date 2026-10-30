import sys
from PyQt6.QtWidgets import QApplication
from gui import MainAppWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Запрещаем автозакрытие приложения диалогами
    app.setQuitOnLastWindowClosed(False)
    
    window = MainAppWindow()
    window.show()
    
    # Принудительно выходим из системы, если окно закрыто пользователем
    window.destroyed.connect(sys.exit)
    
    sys.exit(app.exec())
