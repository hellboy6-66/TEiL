"""
Каталог команд TEiL и исполнитель безопасных команд.
"""

import os
import re
import shlex
import subprocess


CATEGORIES = {
    "Основные": [
        {"name": "pwd",      "desc": "Показать текущую директорию", "instant": True},
        {"name": "whoami",   "desc": "Имя текущего пользователя",   "instant": True},
        {"name": "date",     "desc": "Текущая дата и время",        "instant": True},
        {"name": "hostname", "desc": "Имя хоста",
         "flags": ["-f", "-I"]},
        {"name": "echo",     "desc": "Вывести строку",
         "arg_placeholder": "текст"},
    ],

    "Файлы и папки": [
        {"name": "ls", "desc": "Список файлов",
         "flags": ["-l", "-a", "-h"],
         "arg_placeholder": "путь (необязательно)"},
        {"name": "cd", "desc": "Сменить директорию",
         "arg_placeholder": "путь (например /tmp)"},
        {"name": "df", "desc": "Свободное место на дисках",
         "flags": ["-h", "-T"]},
        {"name": "du", "desc": "Размер директории",
         "flags": ["-s", "-h"],
         "arg_placeholder": "путь"},
        {"name": "find", "desc": "Поиск файлов",
         "arg_placeholder": ". -maxdepth 1 -type f"},
        {"name": "file", "desc": "Определить тип файла по содержимому",
         "flags": ["-b", "-i", "-L"],
         "arg_placeholder": "файл (например note.txt)"},
        {"name": "stat", "desc": "Подробная информация о файле (права, дата, размер)",
         "flags": ["-t", "-f", "-L"],
         "arg_placeholder": "файл (например note.txt)"},
        {"name": "which", "desc": "Показать путь к исполняемому файлу команды",
         "flags": ["-a"],
         "arg_placeholder": "команда (например ls)"},
        {"name": "cat", "desc": "Содержимое файла",
         "arg_placeholder": "файл (например /etc/os-release)"},
        {"name": "head", "desc": "Первые строки файла",
         "arg_placeholder": "-n 10 файл (по умолчанию 10 строк)"},
        {"name": "tail", "desc": "Последние строки файла",
         "arg_placeholder": "-n 10 файл (по умолчанию 10 строк)"},
        {"name": "grep", "desc": "Поиск по шаблону",
         "flags": ["-i", "-n", "-r"],
         "arg_placeholder": "шаблон [файл] (например root /etc/passwd)"},
        {"name": "wc", "desc": "Подсчёт строк, слов и символов",
         "flags": ["-l", "-w", "-c"],
         "arg_placeholder": "файл (например note.txt)"},
        {"name": "sort", "desc": "Сортировка строк текста (вывод в консоль)",
         "flags": ["-r", "-n", "-u"],
         "arg_placeholder": "файл (например note.txt)"},
        {"name": "uniq", "desc": "Удаление повторяющихся строк (вывод в консоль)",
         "arg_placeholder": "файл (например sorted.txt)"},
        {"name": "cut", "desc": "Вырезание колонок из текста (укажите разделитель и номер колонки)",
         "arg_placeholder": "-d ' ' -f 1 файл.txt (разделитель и поле)"},
        {"name": "touch", "desc": "Создать пустой файл (поддерживает скобки {1..3})",
         "arg_placeholder": "имя файла (например file{1..3}.txt)",
         "safe_handler": "touch"},
        {"name": "mkdir", "desc": "Создать каталог (только внутри текущей директории)",
         "flags": ["-p"],
         "arg_placeholder": "имя каталога (например new_folder)",
         "safe_handler": "mkdir"},
        {"name": "mv", "desc": "Переместить/переименовать (только внутри текущей директории)",
         "arg_placeholder": "источник назначение (например note.txt notes/note.txt)",
         "safe_handler": "mv"},
        {"name": "cp", "desc": "Копировать (только внутри текущей директории)",
         "flags": ["-r"],
         "arg_placeholder": "источник назначение (например note.txt notes/copy.txt)",
         "safe_handler": "cp"},
        {"name": "rm", "desc": "Удалить файл или пустой каталог "
                               "(только внутри текущей директории, с подтверждением)",
         "arg_placeholder": "файл или каталог (например note.txt)",
         "safe_handler": "rm"},
    ],

    "Сеть": [
        {"name": "ip", "desc": "Сетевые интерфейсы",
         "arg_placeholder": "addr / route / link"},
        {"name": "ping", "desc": "Проверка связи",
         "flags": ["-c 2", "-c 4", "-c 10"],
         "arg_placeholder": "хост (например 8.8.8.8)"},
        {"name": "curl", "desc": "HTTP-запрос",
         "flags": ["-s", "-I", "-L"],
         "arg_placeholder": "URL"},
    ],

    "Процессы": [
        {"name": "ps", "desc": "Список процессов",
         "flags": ["aux", "-ef"]},
        {"name": "uptime", "desc": "Время работы системы", "instant": True},
        {"name": "free", "desc": "Использование памяти",
         "flags": ["-h", "-m"]},
    ],

    "Система": [
        {"name": "uname", "desc": "Информация о ядре",
         "flags": ["-a", "-r", "-s"]},
        {"name": "lscpu", "desc": "Информация о CPU", "instant": True},
    ],
}


class CommandExecutor:
    """Выполняет безопасные команды и следит за текущей директорией."""

    TIMEOUT = 10

    def __init__(self, start_dir: str | None = None):
        self.cwd = start_dir or os.path.expanduser("~")

    # ------------------------------------------------ парсинг аргументов
    def _parse_args(self, arg_str: str) -> list[str]:
        """Безопасно разбивает строку на аргументы, учитывая кавычки."""
        try:
            return shlex.split(arg_str)
        except ValueError:
            return arg_str.split()

    # ------------------------------------------------ обычное выполнение
    def execute(self, cmd: str) -> str:
        try:
            result = subprocess.run(
                cmd, shell=True, cwd=self.cwd,
                capture_output=True, text=True, timeout=self.TIMEOUT,
                stdin=subprocess.DEVNULL,
            )
            out = result.stdout
            if result.stderr:
                out += result.stderr
            if not out.strip():
                out = "[команда выполнена без вывода]"
            return out
        except subprocess.TimeoutExpired:
            return f"[!] Команда превысила лимит времени ({self.TIMEOUT} с)"
        except Exception as e:
            return f"[!] Ошибка выполнения: {e}"

    # ------------------------------------------------ смена директории
    def change_dir(self, path: str) -> tuple[bool, str]:
        parts = self._parse_args(path)
        if not parts:
            return False, "cd: не указан каталог"
        path = parts[0]
        
        path = os.path.expanduser(path)
        new = path if os.path.isabs(path) else os.path.join(self.cwd, path)
        new = os.path.normpath(new)
        if os.path.isdir(new):
            self.cwd = new
            return True, ""
        return False, f"cd: нет такого каталога: {path}"

    # ------------------------------------------------ эмуляция фигурных скобок
    def _expand_braces(self, text: str) -> list[str]:
        match = re.search(r'\{([^{}]+)\}', text)
        if not match:
            return [text]
        
        content = match.group(1)
        start, end = match.span()
        items = []
        
        if '..' in content:
            parts = content.split('..')
            if len(parts) == 2:
                p1, p2 = parts[0].strip(), parts[1].strip()
                if p1.isdigit() and p2.isdigit():
                    step = 1 if int(p1) <= int(p2) else -1
                    items = [str(i) for i in range(int(p1), int(p2) + step, step)]
                elif len(p1) == 1 and len(p2) == 1 and p1.isalpha() and p2.isalpha():
                    step = 1 if ord(p1) <= ord(p2) else -1
                    items = [chr(c) for c in range(ord(p1), ord(p2) + step, step)]
        else:
            items = content.split(',')
            
        if not items:
            return [text]
            
        results = []
        for item in items:
            new_text = text[:start] + item + text[end:]
            results.extend(self._expand_braces(new_text))
        return results

    # ------------------------------------------------ безопасный touch
    def safe_touch(self, target: str) -> str:
        raw_tokens = self._parse_args(target)
        if not raw_tokens:
            return "touch: не указан файл"

        final_targets = []
        for token in raw_tokens:
            final_targets.extend(self._expand_braces(token))

        cwd_real = os.path.realpath(self.cwd)
        success_count = 0
        errors = []

        for t in final_targets:
            raw_abs = os.path.normpath(os.path.join(cwd_real, os.path.expanduser(t)))

            if not raw_abs.startswith(cwd_real + os.sep):
                errors.append(f"touch: отказ для '{t}' — путь вне текущей директории")
                continue

            try:
                parent = os.path.dirname(raw_abs)
                if not os.path.isdir(parent):
                    errors.append(f"touch: нет такого каталога для '{t}': {parent}")
                    continue
                
                with open(raw_abs, "a"):
                    pass
                os.utime(raw_abs, None)
                success_count += 1
            except PermissionError:
                errors.append(f"touch: '{t}': нет прав на запись")
            except Exception as e:
                errors.append(f"touch: ошибка при создании '{t}': {e}")

        result = []
        if success_count > 0:
            result.append(f"touch: успешно создано/обновлено файлов: {success_count}")
        if errors:
            result.extend(errors)
            
        return "\n".join(result)

    # ------------------------------------------------ безопасный mkdir
    def safe_mkdir(self, target: str, parents: bool) -> str:
        parts = self._parse_args(target)
        if not parts:
            return "mkdir: не указан каталог"
        if len(parts) > 1:
            return "mkdir: одновременное создание нескольких каталогов не поддерживается"
        
        target = parts[0]
        cwd_real = os.path.realpath(self.cwd)
        raw_abs = os.path.normpath(os.path.join(cwd_real, os.path.expanduser(target)))

        if not raw_abs.startswith(cwd_real + os.sep):
            return (f"mkdir: отказ — путь вне текущей директории:\n"
                    f"    {raw_abs}\n"
                    f"mkdir: используйте cd, чтобы перейти в нужный каталог")

        if os.path.isdir(raw_abs) or os.path.exists(raw_abs):
            return f"mkdir: невозможно создать каталог '{target}': Файл существует"

        try:
            if parents:
                os.makedirs(raw_abs, exist_ok=False)
            else:
                parent = os.path.dirname(raw_abs)
                if not os.path.isdir(parent):
                    return (f"mkdir: не удаётся создать каталог '{target}': "
                            f"Нет такого файла или каталога")
                os.mkdir(raw_abs)
            return f"mkdir: каталог создан: {target}"
        except FileExistsError:
            return f"mkdir: невозможно создать каталог '{target}': Файл существует"
        except PermissionError:
            return f"mkdir: '{target}': нет прав на создание"
        except Exception as e:
            return f"mkdir: ошибка: {e}"

    # ------------------------------------------------ безопасный mv
    def safe_mv(self, args: str) -> str:
        parts = self._parse_args(args)
        if len(parts) != 2:
            return ("mv: укажите ровно два аргумента (источник и назначение)\n"
                    "например: mv \"my file.txt\" notes/")

        src_arg, dst_arg = parts[0], parts[1]
        cwd_real = os.path.realpath(self.cwd)
        src_abs = os.path.normpath(os.path.join(cwd_real, os.path.expanduser(src_arg)))
        dst_abs = os.path.normpath(os.path.join(cwd_real, os.path.expanduser(dst_arg)))

        if not src_abs.startswith(cwd_real + os.sep):
            return f"mv: отказ — источник вне текущей директории:\n    {src_abs}"
        if not dst_abs.startswith(cwd_real + os.sep):
            return f"mv: отказ — назначение вне текущей директории:\n    {dst_abs}"
        if not (os.path.exists(src_abs) or os.path.islink(src_abs)):
            return f"mv: невозможно переместить '{src_arg}': Нет такого файла или каталога"
        if src_abs == cwd_real:
            return "mv: отказ — нельзя переместить текущую директорию"
        if dst_abs == src_abs:
            return f"mv: '{src_arg}' и '{dst_arg}' — один и тот же путь"
        if dst_abs.startswith(src_abs + os.sep):
            return "mv: отказ — нельзя переместить каталог внутрь самого себя"

        if os.path.isdir(dst_abs) and not os.path.islink(dst_abs):
            final_dst = os.path.join(dst_abs, os.path.basename(src_abs))
        else:
            final_dst = dst_abs

        if os.path.exists(final_dst) or os.path.islink(final_dst):
            return f"mv: отказ — назначение уже существует:\n    {final_dst}"

        dst_parent = os.path.dirname(final_dst)
        if not os.path.isdir(dst_parent):
            return f"mv: не удаётся переместить в '{dst_arg}': Нет такого каталога: {dst_parent}"

        src_real = os.path.realpath(src_abs)
        if src_real != src_abs and not os.path.islink(src_abs):
            return f"mv: отказ — источник содержит симлинк наружу:\n    {src_abs} -> {src_real}"

        try:
            os.rename(src_abs, final_dst)
            if os.path.isdir(dst_abs) and not os.path.islink(dst_abs) and dst_abs != final_dst:
                return f"mv: '{src_arg}' -> '{os.path.relpath(final_dst, cwd_real)}'"
            return f"mv: перемещено: {src_arg} -> {dst_arg}"
        except OSError:
            try:
                import shutil
                shutil.move(src_abs, final_dst)
                return f"mv: перемещено: {src_arg} -> {dst_arg}"
            except Exception as e2:
                return f"mv: ошибка: {e2}"
        except PermissionError:
            return f"mv: '{src_arg}': нет прав на перемещение"
        except Exception as e:
            return f"mv: ошибка: {e}"

    # ------------------------------------------------ безопасный cp
    def safe_cp(self, args: str, recursive: bool) -> str:
        parts = self._parse_args(args)
        if len(parts) != 2:
            return ("cp: укажите ровно два аргумента (источник и назначение)\n"
                    "например: cp \"my file.txt\" copy.txt")

        src_arg, dst_arg = parts[0], parts[1]
        cwd_real = os.path.realpath(self.cwd)
        src_abs = os.path.normpath(os.path.join(cwd_real, os.path.expanduser(src_arg)))
        dst_abs = os.path.normpath(os.path.join(cwd_real, os.path.expanduser(dst_arg)))

        if not src_abs.startswith(cwd_real + os.sep):
            return f"cp: отказ — источник вне текущей директории:\n    {src_abs}"
        if not dst_abs.startswith(cwd_real + os.sep):
            return f"cp: отказ — назначение вне текущей директории:\n    {dst_abs}"
        if not (os.path.exists(src_abs) or os.path.islink(src_abs)):
            return f"cp: невозможно скопировать '{src_arg}': Нет такого файла или каталога"
        if dst_abs == src_abs:
            return f"cp: '{src_arg}' и '{dst_arg}' — один и тот же путь"
        if dst_abs.startswith(src_abs + os.sep):
            return "cp: отказ — нельзя скопировать каталог внутрь самого себя"

        if os.path.isdir(dst_abs) and not os.path.islink(dst_abs):
            final_dst = os.path.join(dst_abs, os.path.basename(src_abs))
        else:
            final_dst = dst_abs

        if os.path.exists(final_dst) or os.path.islink(final_dst):
            return f"cp: отказ — назначение уже существует:\n    {final_dst}"

        dst_parent = os.path.dirname(final_dst)
        if not os.path.isdir(dst_parent):
            return f"cp: не удаётся скопировать в '{dst_arg}': Нет такого каталога: {dst_parent}"

        src_real = os.path.realpath(src_abs)
        if src_real != src_abs and not os.path.islink(src_abs):
            return f"cp: отказ — источник содержит симлинк наружу:\n    {src_abs} -> {src_real}"

        try:
            import shutil
            if os.path.isdir(src_abs) and not os.path.islink(src_abs):
                if not recursive:
                    return f"cp: '{src_arg}': это каталог (отметьте -r)"
                shutil.copytree(src_abs, final_dst, symlinks=True)
                return f"cp: каталог скопирован: {src_arg} -> {dst_arg}"
            else:
                shutil.copy2(src_abs, final_dst, follow_symlinks=False)
                return f"cp: файл скопирован: {src_arg} -> {dst_arg}"
        except PermissionError:
            return f"cp: '{src_arg}': нет прав на копирование"
        except Exception as e:
            return f"cp: ошибка: {e}"

    # ------------------------------------------------ описание цели для rm
    def describe_target(self, target: str) -> tuple[bool, str]:
        parts = self._parse_args(target)
        if len(parts) == 0:
            return False, "не указан файл или каталог"
        if len(parts) > 1:
            return False, "удаление нескольких объектов одновременно запрещено"
            
        target = parts[0]
        cwd_real = os.path.realpath(self.cwd)
        raw_abs = os.path.normpath(os.path.join(cwd_real, os.path.expanduser(target)))

        if not raw_abs.startswith(cwd_real + os.sep):
            return False, f"путь вне текущей директории:\n{raw_abs}"
        if raw_abs == cwd_real:
            return False, "нельзя удалить текущую директорию"
        if not (os.path.exists(raw_abs) or os.path.islink(raw_abs)):
            return False, f"нет такого файла или каталога: {target}"

        if os.path.islink(raw_abs):
            try:
                pointed = os.readlink(raw_abs)
            except Exception:
                pointed = "?"
            return True, f"символическая ссылка:\n{raw_abs} -> {pointed}"

        if os.path.isfile(raw_abs):
            try:
                size = os.path.getsize(raw_abs)
            except Exception:
                size = 0
            return True, f"файл ({self._human_size(size)}):\n{raw_abs}"

        if os.path.isdir(raw_abs):
            try:
                items = os.listdir(raw_abs)
            except Exception:
                items = []
            if items:
                return False, (
                    f"каталог НЕ пуст ({len(items)} элементов):\n{raw_abs}\n"
                    f"удаление непустых каталогов запрещено"
                )
            return True, f"пустой каталог:\n{raw_abs}"

        return False, f"неизвестный тип файла:\n{raw_abs}"

    @staticmethod
    def _human_size(n: int) -> str:
        if n < 1024: return f"{n} B"
        for unit in ("KB", "MB", "GB", "TB"):
            n /= 1024
            if n < 1024: return f"{n:.1f} {unit}"
        return f"{n:.1f} PB"

    # ------------------------------------------------ безопасный rm
    def safe_rm(self, target: str) -> str:
        parts = self._parse_args(target)
        if len(parts) == 0:
            return "rm: не указан файл или каталог"
        if len(parts) > 1:
            return "rm: удаление нескольких объектов одновременно запрещено"
            
        target = parts[0]
        cwd_real = os.path.realpath(self.cwd)
        raw_abs = os.path.normpath(os.path.join(cwd_real, os.path.expanduser(target)))

        if not raw_abs.startswith(cwd_real + os.sep):
            return f"rm: отказ — путь вне текущей директории:\n    {raw_abs}"
        if raw_abs == cwd_real:
            return "rm: отказ — нельзя удалить текущую директорию"
        if not (os.path.exists(raw_abs) or os.path.islink(raw_abs)):
            return f"rm: '{target}': нет такого файла или каталога"

        real_abs = os.path.realpath(raw_abs)
        if real_abs != raw_abs and not os.path.islink(raw_abs):
            return f"rm: отказ — в пути есть симлинк, ведущий за пределы рабочей области:\n    {raw_abs} -> {real_abs}"

        try:
            if os.path.islink(raw_abs) or os.path.isfile(raw_abs):
                os.unlink(raw_abs)
                return f"rm: удалён файл: {target}"
            if os.path.isdir(raw_abs):
                try:
                    os.rmdir(raw_abs)
                    return f"rm: удалён пустой каталог: {target}"
                except OSError:
                    return f"rm: '{target}': каталог не пуст. Удаление непустых каталогов запрещено"
            return f"rm: '{target}': неизвестный тип файла"
        except PermissionError:
            return f"rm: '{target}': нет прав на удаление"
        except Exception as e:
            return f"rm: ошибка: {e}"