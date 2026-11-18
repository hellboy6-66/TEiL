"""Фоновые потоки для TEiL."""

from PyQt6.QtCore import QThread, pyqtSignal

class CommandWorker(QThread):
    """Поток для выполнения команд без зависания интерфейса."""
    result_ready = pyqtSignal(str)

    def __init__(self, func, *args):
        super().__init__()
        self.func = func
        self.args = args

    def run(self):
        try:
            result = self.func(*self.args)
            self.result_ready.emit(result)
        except Exception as e:
            self.result_ready.emit(f"[!] Ошибка в потоке: {e}")