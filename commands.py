import os
import subprocess
from PyQt6.QtWidgets import QInputDialog, QMessageBox

class TerminalCommands:
    def __init__(self):
        self.dir_stack = []
        self.previous_working_dir = None

    def handle_cd(self, parent_window, callback_update_label):
        text, ok = QInputDialog.getText(parent_window, "Смена директории", "Введите новый путь к директории:")
        if ok and text.strip():
            path_to_check = text.strip()
            if os.path.isdir(path_to_check):
                self.previous_working_dir = os.getcwd()
                os.chdir(path_to_check)
                callback_update_label(os.getcwd())
            else:
                QMessageBox.warning(parent_window, "Ошибка", f"Директория не найдена:\n{path_to_check}")

    def handle_ls(self, parent_window):
        keys, ok = QInputDialog.getText(parent_window, "Параметры ls", "Введите ключи терминала (например: -l, -a, -la) или оставьте пустым:")
        if ok:
            keys = keys.strip()
            command = ["ls"]
            if keys:
                command.extend(keys.split())
            try:
                result = subprocess.check_output(command, cwd=os.getcwd(), text=True, stderr=subprocess.STDOUT)
                if not result.strip():
                    result = "(Директория пуста)"
                QMessageBox.information(parent_window, f"Результат: ls {keys}", result)
            except subprocess.CalledProcessError as e:
                QMessageBox.critical(parent_window, "Ошибка терминала", f"Команда завершилась с ошибкой:\n{e.output}")
            except Exception as e:
                QMessageBox.critical(parent_window, "Критическая ошибка", f"Не удалось выполнить команду:\n{str(e)}")

    def handle_touch(self, parent_window):
        filename, ok = QInputDialog.getText(
            parent_window, 
            "Команда touch", 
            "Введите имя файла или несколько имен через пробел (например: a.txt b.py c.log):"
        )
        if ok and filename.strip():
            # Разделяем введенную строку по пробелам на список отдельных файлов
            file_list = filename.strip().split()
            
            created_files = []
            updated_files = []
            failed_files = []

            for file_name in file_list:
                try:
                    if os.path.exists(file_name):
                        os.utime(file_name, None)
                        updated_files.append(file_name)
                    else:
                        with open(file_name, 'a'):
                            pass
                        created_files.append(file_name)
                except Exception as e:
                    failed_files.append(f"{file_name} ({str(e)})")

            # Формируем красивый отчет для пользователя
            report = []
            if created_files:
                report.append(f"Создано файлов ({len(created_files)}):\n" + ", ".join(created_files))
            if updated_files:
                report.append(f"Обновлено время ({len(updated_files)}):\n" + ", ".join(updated_files))
            if failed_files:
                report.append(f"Ошибка при создании ({len(failed_files)}):\n" + "\n".join(failed_files))

            QMessageBox.information(parent_window, "Результат touch", "\n\n".join(report))

    def handle_pushd(self, parent_window, callback_update_label):
        text, ok = QInputDialog.getText(parent_window, "Команда pushd", "Введите путь к новой директории для перехода:")
        if ok and text.strip():
            path_to_check = text.strip()
            if os.path.isdir(path_to_check):
                self.previous_working_dir = os.getcwd()
                self.dir_stack.append(os.getcwd())
                os.chdir(path_to_check)
                callback_update_label(os.getcwd())
                current_stack_str = " -> ".join([os.getcwd()] + self.dir_stack[::-1])
                QMessageBox.information(parent_window, "pushd", f"Директория добавлена в стек.\nТекущий стек:\n{current_stack_str}")
            else:
                QMessageBox.warning(parent_window, "Ошибка pushd", f"Директория не найдена:\n{path_to_check}")

    def handle_popd(self, parent_window, callback_update_label):
        if self.dir_stack:
            self.previous_working_dir = os.getcwd()
            previous_dir = self.dir_stack.pop()
            os.chdir(previous_dir)
            callback_update_label(os.getcwd())
            QMessageBox.information(parent_window, "popd", f"Вернулись назад в:\n{previous_dir}")
        else:
            QMessageBox.warning(parent_window, "Ошибка popd", "Стек директорий пуст! (directory stack empty)")

    def handle_dirs(self, parent_window):
        if not self.dir_stack:
            QMessageBox.information(parent_window, "dirs", f"Стек пуст. Текущая папка:\n{os.getcwd()}")
        else:
            stack_list = [os.getcwd()] + self.dir_stack[::-1]
            formatted_stack = "\n".join([f"[{i}] {path}" for i, path in enumerate(stack_list)])
            QMessageBox.information(parent_window, "Стек директорий (dirs)", formatted_stack)

    def handle_cd_minus(self, parent_window, callback_update_label):
        if self.previous_working_dir is None:
            QMessageBox.warning(parent_window, "cd -", "Предыдущая директория отсутствует (OLDPWD не задан)")
        else:
            temp_current = os.getcwd()
            os.chdir(self.previous_working_dir)
            callback_update_label(os.getcwd())
            QMessageBox.information(parent_window, "cd -", f"Перешли в предыдущую директорию:\n{os.getcwd()}")
            self.previous_working_dir = temp_current

    def handle_find(self, parent_window):
        filename, ok = QInputDialog.getText(parent_window, "Команда find", "Введите имя файла или маску для поиска (например: *.txt или main.py):")
        if ok and filename.strip():
            command = ["find", ".", "-name", filename.strip()]
            try:
                result = subprocess.check_output(command, cwd=os.getcwd(), text=True, stderr=subprocess.STDOUT)
                if not result.strip():
                    result = "Файлы не найдены."
                else:
                    lines = result.splitlines()
                    if len(lines) > 30:
                        result = "\n".join(lines[:30]) + f"\n\n... и еще {len(lines) - 30} строк (показаны первые 30 результатов)."
                QMessageBox.information(parent_window, "Результат find", result)
            except subprocess.CalledProcessError as e:
                QMessageBox.critical(parent_window, "Ошибка find", f"Команда завершилась с ошибкой:\n{e.output}")

    def handle_locate(self, parent_window):
        filename, ok = QInputDialog.getText(parent_window, "Команда locate", "Введите ключевое слово для глобального поиска по системе:")
        if ok and filename.strip():
            command = ["locate", filename.strip()]
            try:
                result = subprocess.check_output(command, text=True, stderr=subprocess.STDOUT)
                if not result.strip():
                    result = "Ничего не найдено в базе данных системы."
                lines = result.splitlines()
                if len(lines) > 30:
                    result = "\n".join(lines[:30]) + f"\n\n... и еще {len(lines) - 30} строк (показаны первые 30 результатов)."
                QMessageBox.information(parent_window, "Результат locate", result)
            except subprocess.CalledProcessError:
                QMessageBox.warning(parent_window, "Предупреждение locate", "Ничего не найдено или утилита locate не установлена.")
            except Exception as e:
                QMessageBox.critical(parent_window, "Ошибка", f"Не удалось выполнить поиск:\n{str(e)}")
