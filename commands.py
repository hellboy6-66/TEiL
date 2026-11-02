import os
import re
import shutil
import subprocess
# Добавили QDialog, QVBoxLayout, QPlainTextEdit, QPushButton для окна less
from PyQt6.QtWidgets import (QInputDialog, QMessageBox, QDialog, 
                             QVBoxLayout, QPlainTextEdit, QPushButton)

class TerminalCommands:
    def __init__(self):
        self.dir_stack = []
        self.previous_working_dir = None

    def _expand_braces(self, text):
        """Внутренняя функция парсинга фигурных скобок (Brace Expansion)"""
        match = re.search(r'\{([^}]+)\}', text)
        if not match:
            return [text]
        
        prefix = text[:match.start()]
        suffix = text[match.end():]
        body = match.group(1)
        
        expanded = []
        if '..' in body:
            parts = body.split('..')
            if len(parts) == 2:
                start, end = parts[0], parts[1]
                if start.isdigit() and end.isdigit():
                    for i in range(int(start), int(end) + 1):
                        expanded.extend(self._expand_braces(f"{prefix}{i}{suffix}"))
                elif len(start) == 1 and len(end) == 1:
                    for ord_char in range(ord(start), ord(end) + 1):
                        expanded.extend(self._expand_braces(f"{prefix}{chr(ord_char)}{suffix}"))
        else:
            items = body.split(',')
            for item in items:
                expanded.extend(self._expand_braces(f"{prefix}{item.strip()}{suffix}"))
        return expanded

    def _parse_input_to_list(self, raw_input):
        final_list = []
        for part in raw_input.strip().split():
            final_list.extend(self._expand_braces(part))
        return final_list

    def handle_cd(self, parent_window, callback_update_label, print_out):
        text, ok = QInputDialog.getText(parent_window, "Смена директории", "Введите новый путь к директории:")
        if ok and text.strip():
            path_to_check = text.strip()
            if os.path.isdir(path_to_check):
                self.previous_working_dir = os.getcwd()
                os.chdir(path_to_check)
                callback_update_label(os.getcwd())
                print_out(f"Переход в директорию: {os.getcwd()}")
            else:
                print_out(f"cd: {path_to_check}: Нет такого файла или каталога")

    def handle_ls(self, parent_window, print_out):
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
                print_out(result)
            except subprocess.CalledProcessError as e:
                print_out(f"Ошибка выполнения ls:\n{e.output}")
            except Exception as e:
                print_out(f"Критическая ошибка ls:\n{str(e)}")

    def handle_touch(self, parent_window, print_out):
        filename, ok = QInputDialog.getText(
            parent_window, 
            "Команда touch", 
            "Введите имена файлов (поддерживаются скобки {}, например: file{1..3}.txt):"
        )
        if ok and filename.strip():
            file_list = self._parse_input_to_list(filename)
            created_files, updated_files, failed_files = [], [], []

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

            if created_files: print_out(f"Создано файлов ({len(created_files)}):\n" + ", ".join(created_files))
            if updated_files: print_out(f"Обновлено время ({len(updated_files)}):\n" + ", ".join(updated_files))
            if failed_files: print_out(f"Ошибки ({len(failed_files)}):\n" + "\n".join(failed_files))

    def handle_mkdir(self, parent_window, print_out):
        dirname, ok = QInputDialog.getText(
            parent_window, 
            "Команда mkdir", 
            "Введите имена директорий (поддерживаются скобки {}):"
        )
        if ok and dirname.strip():
            dir_list = self._parse_input_to_list(dirname)
            created_dirs, exist_dirs, failed_dirs = [], [], []

            for d_name in dir_list:
                try:
                    if os.path.exists(d_name):
                        exist_dirs.append(d_name)
                    else:
                        os.makedirs(d_name, exist_ok=True)
                        created_dirs.append(d_name)
                except Exception as e:
                    failed_dirs.append(f"{d_name} ({str(e)})")

            if created_dirs: print_out(f"Создано директорий ({len(created_dirs)}):\n" + ", ".join(created_dirs))
            if exist_dirs: print_out(f"Уже существуют ({len(exist_dirs)}):\n" + ", ".join(exist_dirs))
            if failed_dirs: print_out(f"Ошибки при создании ({len(failed_dirs)}):\n" + "\n".join(failed_dirs))

    def handle_cp(self, parent_window, print_out):
        source, ok = QInputDialog.getText(parent_window, "Команда cp", "Введите источник (файл/директорию) или {}:")
        if not (ok and source.strip()): return

        dest, ok = QInputDialog.getText(parent_window, "Команда cp", "Введите назначение (файл или директорию):")
        if not (ok and dest.strip()): return

        source_list = self._parse_input_to_list(source)
        dest = dest.strip()

        dirs_in_sources = [s for s in source_list if os.path.isdir(s)]
        recursive = False
        if dirs_in_sources:
            reply = QMessageBox.question(
                parent_window, "cp: рекурсивное копирование",
                "Среди источников есть директории.\nКопировать рекурсивно (аналог cp -r)?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes: return
            recursive = True

        copied, failed = [], []
        multiple = len(source_list) > 1

        for src in source_list:
            try:
                if not os.path.exists(src):
                    failed.append(f"{src} (источник не найден)")
                    continue
                if os.path.isdir(src):
                    if not recursive:
                        failed.append(f"{src} (это директория, пропущено)")
                        continue
                    target = os.path.join(dest, os.path.basename(os.path.normpath(src))) if os.path.isdir(dest) else dest
                    shutil.copytree(src, target, dirs_exist_ok=True)
                    copied.append(f"{src} -> {target}/")
                else:
                    if os.path.isdir(dest):
                        target = os.path.join(dest, os.path.basename(src))
                    elif multiple:
                        failed.append(f"{src} (несколько источников — назначение должно быть директорией)")
                        continue
                    else:
                        target = dest
                    shutil.copy2(src, target)
                    copied.append(f"{src} -> {target}")
            except Exception as e:
                failed.append(f"{src} ({str(e)})")

        if copied: print_out(f"Скопировано ({len(copied)}):\n" + "\n".join(copied))
        if failed: print_out(f"Ошибки cp ({len(failed)}):\n" + "\n".join(failed))

    def handle_mv(self, parent_window, print_out):
        source, ok = QInputDialog.getText(parent_window, "Команда mv", "Введите источник (файл/директорию) или {}:")
        if not (ok and source.strip()): return

        dest, ok = QInputDialog.getText(parent_window, "Команда mv", "Введите назначение (новое имя или существующую директорию):")
        if not (ok and dest.strip()): return

        source_list = self._parse_input_to_list(source)
        dest = dest.strip()

        moved, failed = [], []
        multiple = len(source_list) > 1

        for src in source_list:
            try:
                if not os.path.exists(src):
                    failed.append(f"{src} (источник не найден)")
                    continue
                if os.path.isdir(dest):
                    target = os.path.join(dest, os.path.basename(os.path.normpath(src)))
                elif multiple:
                    failed.append(f"{src} (несколько источников — назначение должно быть директорией)")
                    continue
                else:
                    target = dest

                if os.path.isdir(src) and os.path.abspath(target).startswith(os.path.abspath(src) + os.sep):
                    failed.append(f"{src} (нельзя переместить директорию внутрь себя)")
                    continue

                shutil.move(src, target)
                moved.append(f"{src} -> {target}")
            except Exception as e:
                failed.append(f"{src} ({str(e)})")

        if moved: print_out(f"Перемещено ({len(moved)}):\n" + "\n".join(moved))
        if failed: print_out(f"Ошибки mv ({len(failed)}):\n" + "\n".join(failed))

    def handle_rm(self, parent_window, print_out):
        target, ok = QInputDialog.getText(parent_window, "Команда rm", "Введите имя файла/директории для удаления или {}:")
        if not (ok and target.strip()): return

        target_list = self._parse_input_to_list(target)

        dirs_in_targets = [t for t in target_list if os.path.isdir(t)]
        recursive = False
        if dirs_in_targets:
            reply = QMessageBox.question(
                parent_window, "rm: рекурсивное удаление",
                "Среди целей есть директории.\nУдалить их рекурсивно (аналог rm -r)?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes: return
            recursive = True

        preview = "\n".join(f"  • {t}" for t in target_list)
        confirm = QMessageBox.warning(
            parent_window, "Подтверждение удаления",
            f"Вы действительно хотите удалить следующие объекты?\n\n{preview}\n\nЭто действие необратимо!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if confirm != QMessageBox.StandardButton.Yes: return

        removed_files, removed_dirs, failed = [], [], []

        for t in target_list:
            try:
                if not os.path.exists(t):
                    failed.append(f"{t} (не найдено)")
                    continue
                if os.path.isdir(t):
                    if not recursive:
                        failed.append(f"{t} (это директория, нужен -r)")
                        continue
                    shutil.rmtree(t)
                    removed_dirs.append(t)
                else:
                    os.remove(t)
                    removed_files.append(t)
            except Exception as e:
                failed.append(f"{t} ({str(e)})")

        if removed_files: print_out(f"Удалено файлов ({len(removed_files)}):\n" + "\n".join(removed_files))
        if removed_dirs: print_out(f"Удалено директорий ({len(removed_dirs)}):\n" + "\n".join(removed_dirs))
        if failed: print_out(f"Ошибки rm ({len(failed)}):\n" + "\n".join(failed))

    def handle_cat(self, parent_window, print_out):
        filename, ok = QInputDialog.getText(parent_window, "Команда cat", "Введите имена файлов для просмотра:")
        if not (ok and filename.strip()): return

        file_list = self._parse_input_to_list(filename)
        output_content, errors = [], []

        for f_name in file_list:
            try:
                if not os.path.exists(f_name):
                    errors.append(f"{f_name}: Нет такого файла или каталога")
                    continue
                if os.path.isdir(f_name):
                    errors.append(f"{f_name}: Это каталог")
                    continue
                
                with open(f_name, 'r', encoding='utf-8', errors='replace') as file:
                    content = file.read()
                    if content: output_content.append(content)
                    else: output_content.append(f"--- (Файл {f_name} пуст) ---")
            except Exception as e:
                errors.append(f"{f_name}: {str(e)}")

        final_text = "".join(output_content)
        if errors:
            if final_text: final_text += "\n\n"
            final_text += "--- ОШИБКИ ---\n" + "\n".join(errors)

        if not final_text.strip(): final_text = "(Нет вывода)"
        print_out(final_text)

    def handle_less(self, parent_window, print_out):
        """Постраничный просмотр файла в отдельном окне (аналог less)"""
        filename, ok = QInputDialog.getText(parent_window, "Команда less", "Введите имя файла для просмотра (или {}):")
        if not (ok and filename.strip()): return

        file_list = self._parse_input_to_list(filename)
        output_content, errors = [], []

        for f_name in file_list:
            try:
                if not os.path.exists(f_name):
                    errors.append(f"{f_name}: Нет такого файла или каталога")
                    continue
                if os.path.isdir(f_name):
                    errors.append(f"{f_name}: Это каталог")
                    continue
                
                with open(f_name, 'r', encoding='utf-8', errors='replace') as file:
                    content = file.read()
                    if content: output_content.append(content)
                    else: output_content.append(f"--- (Файл {f_name} пуст) ---")
            except Exception as e:
                errors.append(f"{f_name}: {str(e)}")

        final_text = "".join(output_content)
        if errors:
            if final_text: final_text += "\n\n"
            final_text += "--- ОШИБКИ ---\n" + "\n".join(errors)

        if not final_text.strip():
            print_out("Файл пуст или не найден.")
            return

        # Создаем отдельное окно (диалог) для less
        dialog = QDialog(parent_window)
        dialog.setWindowTitle(f"less: {filename}")
        dialog.resize(800, 600)  # Размер окна

        layout = QVBoxLayout(dialog)

        # Текстовое поле (только для чтения, с прокруткой)
        text_area = QPlainTextEdit(dialog)
        text_area.setPlainText(final_text)
        text_area.setReadOnly(True)
        text_area.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: 'Courier New', Consolas, monospace;
                font-size: 14px;
                border: none;
            }
        """)

        btn_close = QPushButton("Закрыть", dialog)
        btn_close.clicked.connect(dialog.accept)

        layout.addWidget(text_area)
        layout.addWidget(btn_close)

        # Выводим подтверждение в основную консоль
        print_out(f"Открыт просмотр файла: {filename} (нажмите 'Закрыть' для выхода)")
        
        # Открываем окно (блокирует основной интерфейс до закрытия)
        dialog.exec()

    def handle_pushd(self, parent_window, callback_update_label, print_out):
        text, ok = QInputDialog.getText(parent_window, "Команда pushd", "Введите путь к новой директории для перехода:")
        if ok and text.strip():
            path_to_check = text.strip()
            if os.path.isdir(path_to_check):
                self.previous_working_dir = os.getcwd()
                self.dir_stack.append(os.getcwd())
                os.chdir(path_to_check)
                callback_update_label(os.getcwd())
                current_stack_str = " -> ".join([os.getcwd()] + self.dir_stack[::-1])
                print_out(f"Директория добавлена в стек.\nТекущий стек:\n{current_stack_str}")
            else:
                print_out(f"pushd: {path_to_check}: Нет такого файла или каталога")

    def handle_popd(self, parent_window, callback_update_label, print_out):
        if self.dir_stack:
            self.previous_working_dir = os.getcwd()
            previous_dir = self.dir_stack.pop()
            os.chdir(previous_dir)
            callback_update_label(os.getcwd())
            print_out(f"Вернулись назад в:\n{previous_dir}")
        else:
            print_out("Ошибка popd: Стек директорий пуст!")

    def handle_dirs(self, parent_window, print_out):
        if not self.dir_stack:
            print_out(f"Стек пуст. Текущая папка:\n{os.getcwd()}")
        else:
            stack_list = [os.getcwd()] + self.dir_stack[::-1]
            formatted_stack = "\n".join([f"[{i}] {path}" for i, path in enumerate(stack_list)])
            print_out(formatted_stack)

    def handle_cd_minus(self, parent_window, callback_update_label, print_out):
        if self.previous_working_dir is None:
            print_out("cd -: Предыдущая директория отсутствует (OLDPWD не задан)")
        else:
            temp_current = os.getcwd()
            os.chdir(self.previous_working_dir)
            callback_update_label(os.getcwd())
            print_out(f"Перешли в предыдущую директорию:\n{os.getcwd()}")
            self.previous_working_dir = temp_current

    def handle_find(self, parent_window, print_out):
        filename, ok = QInputDialog.getText(parent_window, "Команда find", "Введите имя файла или маску для поиска (например: *.txt):")
        if ok and filename.strip():
            command = ["find", ".", "-name", filename.strip()]
            try:
                result = subprocess.check_output(command, cwd=os.getcwd(), text=True, stderr=subprocess.STDOUT)
                if not result.strip():
                    print_out("Файлы не найдены.")
                else:
                    print_out(result)
            except subprocess.CalledProcessError as e:
                print_out(f"Ошибка find:\n{e.output}")

    def handle_locate(self, parent_window, print_out):
        filename, ok = QInputDialog.getText(parent_window, "Команда locate", "Введите ключевое слово для глобального поиска:")
        if ok and filename.strip():
            command = ["locate", filename.strip()]
            try:
                result = subprocess.check_output(command, text=True, stderr=subprocess.STDOUT)
                if not result.strip():
                    print_out("Ничего не найдено в базе данных системы.")
                else:
                    print_out(result)
            except subprocess.CalledProcessError:
                print_out("Предупреждение locate: Ничего не найдено или утилита locate не установлена.")
            except Exception as e:
                print_out(f"Ошибка locate:\n{str(e)}")