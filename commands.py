"""
Каталог команд TEiL и исполнитель безопасных команд.

name             — имя (без флагов)
desc             — подсказка
flags            — список галочек; однобуквенные (-a, -l, …) склеиваются в -al
arg_placeholder  — подсказка для поля аргумента
instant          — если True, выполняется без диалога
safe_handler     — имя встроенного безопасного обработчика
                   ("touch", "mkdir", "mv", "cp", "rm")
"""

import os
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
        {"name": "cat", "desc": "Содержимое файла",
         "arg_placeholder": "файл (например /etc/os-release)"},
        {"name": "head", "desc": "Первые строки файла",
         "arg_placeholder": "-n 10 файл (по умолчанию 10 строк)"},
        {"name": "tail", "desc": "Последние строки файла",
         "arg_placeholder": "-n 10 файл (по умолчанию 10 строк)"},
        {"name": "grep", "desc": "Поиск по шаблону",
         "flags": ["-i", "-n", "-r"],
         "arg_placeholder": "шаблон [файл] (например root /etc/passwd)"},
        {"name": "touch", "desc": "Создать пустой файл (только внутри текущей директории)",
         "arg_placeholder": "имя файла (например note.txt)",
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
        path = os.path.expanduser(path.strip())
        new = path if os.path.isabs(path) else os.path.join(self.cwd, path)
        new = os.path.normpath(new)
        if os.path.isdir(new):
            self.cwd = new
            return True, ""
        return False, f"cd: нет такого каталога: {path}"

    # ------------------------------------------------ безопасный touch
    def safe_touch(self, target: str) -> str:
        target = target.strip()
        if not target:
            return "touch: не указан файл"

        cwd_real = os.path.realpath(self.cwd)
        raw_abs = os.path.normpath(os.path.join(cwd_real, os.path.expanduser(target)))

        if not raw_abs.startswith(cwd_real + os.sep):
            return (f"touch: отказ — путь вне текущей директории:\n"
                    f"    {raw_abs}\n"
                    f"touch: используйте cd, чтобы перейти в нужный каталог")

        try:
            parent = os.path.dirname(raw_abs)
            if not os.path.isdir(parent):
                return f"touch: нет такого каталога: {parent}"
            with open(raw_abs, "a"):
                pass
            os.utime(raw_abs, None)
            return f"touch: файл создан/обновлён: {target}"
        except PermissionError:
            return f"touch: '{target}': нет прав на запись"
        except Exception as e:
            return f"touch: ошибка: {e}"

    # ------------------------------------------------ безопасный mkdir
    def safe_mkdir(self, target: str, parents: bool) -> str:
        target = target.strip()
        if not target:
            return "mkdir: не указан каталог"

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
        args = args.strip()
        if not args:
            return "mv: не указаны источник и назначение"

        parts = args.split(None, 1)
        if len(parts) < 2:
            return ("mv: недостаточно аргументов\n"
                    "mv: укажите источник и назначение через пробел, "
                    "например: note.txt notes/note.txt")

        src_arg, dst_arg = parts[0], parts[1].strip()
        if not dst_arg:
            return "mv: не указано назначение"

        cwd_real = os.path.realpath(self.cwd)

        src_abs = os.path.normpath(
            os.path.join(cwd_real, os.path.expanduser(src_arg))
        )
        dst_abs = os.path.normpath(
            os.path.join(cwd_real, os.path.expanduser(dst_arg))
        )

        if not src_abs.startswith(cwd_real + os.sep):
            return (f"mv: отказ — источник вне текущей директории:\n"
                    f"    {src_abs}\n"
                    f"mv: используйте cd, чтобы перейти в нужный каталог")

        if not dst_abs.startswith(cwd_real + os.sep):
            return (f"mv: отказ — назначение вне текущей директории:\n"
                    f"    {dst_abs}\n"
                    f"mv: используйте cd, чтобы перейти в нужный каталог")

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
            return (f"mv: отказ — назначение уже существует:\n"
                    f"    {final_dst}\n"
                    f"mv: перезапись запрещена. Укажите другое имя или удалите цель")

        dst_parent = os.path.dirname(final_dst)
        if not os.path.isdir(dst_parent):
            return (f"mv: не удаётся переместить в '{dst_arg}': "
                    f"Нет такого каталога: {dst_parent}")

        src_real = os.path.realpath(src_abs)
        if src_real != src_abs and not os.path.islink(src_abs):
            return (f"mv: отказ — источник содержит симлинк наружу:\n"
                    f"    {src_abs} -> {src_real}")

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
        args = args.strip()
        if not args:
            return "cp: не указаны источник и назначение"

        parts = args.split(None, 1)
        if len(parts) < 2:
            return ("cp: недостаточно аргументов\n"
                    "cp: укажите источник и назначение через пробел, "
                    "например: note.txt notes/copy.txt")

        src_arg, dst_arg = parts[0], parts[1].strip()
        if not dst_arg:
            return "cp: не указано назначение"

        cwd_real = os.path.realpath(self.cwd)

        src_abs = os.path.normpath(
            os.path.join(cwd_real, os.path.expanduser(src_arg))
        )
        dst_abs = os.path.normpath(
            os.path.join(cwd_real, os.path.expanduser(dst_arg))
        )

        if not src_abs.startswith(cwd_real + os.sep):
            return (f"cp: отказ — источник вне текущей директории:\n"
                    f"    {src_abs}\n"
                    f"cp: используйте cd, чтобы перейти в нужный каталог")

        if not dst_abs.startswith(cwd_real + os.sep):
            return (f"cp: отказ — назначение вне текущей директории:\n"
                    f"    {dst_abs}\n"
                    f"cp: используйте cd, чтобы перейти в нужный каталог")

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
            return (f"cp: отказ — назначение уже существует:\n"
                    f"    {final_dst}\n"
                    f"cp: перезапись запрещена. Укажите другое имя или удалите цель")

        dst_parent = os.path.dirname(final_dst)
        if not os.path.isdir(dst_parent):
            return (f"cp: не удаётся скопировать в '{dst_arg}': "
                    f"Нет такого каталога: {dst_parent}")

        src_real = os.path.realpath(src_abs)
        if src_real != src_abs and not os.path.islink(src_abs):
            return (f"cp: отказ — источник содержит симлинк наружу:\n"
                    f"    {src_abs} -> {src_real}")

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

    # ------------------------------------------------ описание цели для подтверждения
    def describe_target(self, target: str) -> tuple[bool, str]:
        """
        Возвращает (можно_удалить, человекочитаемое_описание).
        Используется GUI для показа диалога подтверждения перед rm.
        """
        target = target.strip()
        if not target:
            return False, "не указан файл или каталог"

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
                    f"удаление непустых каталогов запрещено (нет ключа -r)"
                )
            return True, f"пустой каталог:\n{raw_abs}"

        return False, f"неизвестный тип файла:\n{raw_abs}"

    @staticmethod
    def _human_size(n: int) -> str:
        if n < 1024:
            return f"{n} B"
        for unit in ("KB", "MB", "GB", "TB"):
            n /= 1024
            if n < 1024:
                return f"{n:.1f} {unit}"
        return f"{n:.1f} PB"

    # ------------------------------------------------ безопасный rm (без ключей)
    def safe_rm(self, target: str) -> str:
        target = target.strip()
        if not target:
            return "rm: не указан файл или каталог"

        cwd_real = os.path.realpath(self.cwd)
        raw_abs = os.path.normpath(os.path.join(cwd_real, os.path.expanduser(target)))

        if not raw_abs.startswith(cwd_real + os.sep):
            return (f"rm: отказ — путь вне текущей директории:\n"
                    f"    {raw_abs}\n"
                    f"rm: используйте cd, чтобы перейти в нужный каталог")

        if raw_abs == cwd_real:
            return "rm: отказ — нельзя удалить текущую директорию"

        if not (os.path.exists(raw_abs) or os.path.islink(raw_abs)):
            return f"rm: '{target}': нет такого файла или каталога"

        real_abs = os.path.realpath(raw_abs)
        if real_abs != raw_abs and not os.path.islink(raw_abs):
            return (f"rm: отказ — в пути есть симлинк, ведущий за пределы рабочей области:\n"
                    f"    {raw_abs} -> {real_abs}")

        try:
            if os.path.islink(raw_abs) or os.path.isfile(raw_abs):
                os.unlink(raw_abs)
                return f"rm: удалён файл: {target}"

            if os.path.isdir(raw_abs):
                try:
                    os.rmdir(raw_abs)
                    return f"rm: удалён пустой каталог: {target}"
                except OSError:
                    return (f"rm: '{target}': каталог не пуст\n"
                            f"rm: удаление непустых каталогов запрещено (нет ключа -r)")

            return f"rm: '{target}': неизвестный тип файла"
        except PermissionError:
            return f"rm: '{target}': нет прав на удаление"
        except Exception as e:
            return f"rm: ошибка: {e}"