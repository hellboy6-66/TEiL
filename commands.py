"""
Каталог команд TEiL и исполнитель безопасных команд.

name             — имя (без флагов)
desc             — подсказка
flags            — список галочек; однобуквенные (-a, -l, …) склеиваются в -al
arg_placeholder  — подсказка для поля аргумента
instant          — если True, выполняется без диалога
dangerous        — если True, реально НЕ выполняется
sim              — lambda(cmd) -> str, текст «вывода» для опасных
safe_handler     — имя встроенного безопасного обработчика ("touch", "mkdir", "mv")
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

    "⚠ Опасные": [
        {"name": "rm -rf /", "desc": "Удаление всей файловой системы",
         "dangerous": True,
         "sim": lambda cmd: (
            "[СИМУЛЯЦИЯ] rm -rf /\n"
            "rm: рекурсивное удаление корня '/'\n"
            "rm: удалено 138 402 файла\n"
            "[!] Команда заблокирована TEiL."
         )},
        {"name": "rm -rf /*", "desc": "Удаление содержимого корня",
         "dangerous": True,
         "sim": lambda cmd: (
            "[СИМУЛЯЦИЯ] rm -rf /*\n"
            "rm: удаление /bin /boot /dev /etc /home /lib /usr /var ...\n"
            "[!] Команда заблокирована TEiL."
         )},
        {"name": "dd if=/dev/zero of=/dev/sda", "desc": "Затирание диска нулями",
         "dangerous": True,
         "sim": lambda cmd: (
            "[СИМУЛЯЦИЯ] dd if=/dev/zero of=/dev/sda\n"
            "5368709120 байт (5.4 GB) скопировано\n"
            "[!] Диск /dev/sda был бы полностью уничтожен. TEiL заблокировал команду."
         )},
        {"name": "mkfs.ext4 /dev/sda1", "desc": "Форматирование раздела",
         "dangerous": True,
         "sim": lambda cmd: (
            "[СИМУЛЯЦИЯ] mkfs.ext4 /dev/sda1\n"
            "[!] Раздел /dev/sda1 был бы отформатирован. Команда заблокирована TEiL."
         )},
        {"name": ":(){ :|:& };:", "desc": "Fork-бомба",
         "dangerous": True,
         "sim": lambda cmd: (
            "[СИМУЛЯЦИЯ] fork-бомба\n"
            "bash: fork: retry: Resource temporarily unavailable\n"
            "[!] Система «зависла бы». TEiL заблокировал команду."
         )},
        {"name": "chmod -R 000 /", "desc": "Снятие прав со всей системы",
         "dangerous": True,
         "sim": lambda cmd: (
            "[СИМУЛЯЦИЯ] chmod -R 000 /\n"
            "[!] Команда заблокирована TEiL."
         )},
        {"name": "shutdown -h now", "desc": "Мгновенное выключение",
         "dangerous": True,
         "sim": lambda cmd: (
            "[СИМУЛЯЦИЯ] shutdown -h now\n"
            "[!] Компьютер был бы выключен. TEiL заблокировал команду."
         )},
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

        # 1. Источник внутри cwd
        if not src_abs.startswith(cwd_real + os.sep):
            return (f"mv: отказ — источник вне текущей директории:\n"
                    f"    {src_abs}\n"
                    f"mv: используйте cd, чтобы перейти в нужный каталог")

        # 2. Назначение внутри cwd
        if not dst_abs.startswith(cwd_real + os.sep):
            return (f"mv: отказ — назначение вне текущей директории:\n"
                    f"    {dst_abs}\n"
                    f"mv: используйте cd, чтобы перейти в нужный каталог")

        # 3. Источник существует
        if not (os.path.exists(src_abs) or os.path.islink(src_abs)):
            return f"mv: невозможно переместить '{src_arg}': Нет такого файла или каталога"

        # 4. Источник не совпадает с cwd
        if src_abs == cwd_real:
            return "mv: отказ — нельзя переместить текущую директорию"

        # 5. Источник и назначение не совпадают
        if dst_abs == src_abs:
            return f"mv: '{src_arg}' и '{dst_arg}' — один и тот же путь"

        if dst_abs.startswith(src_abs + os.sep):
            return "mv: отказ — нельзя переместить каталог внутрь самого себя"

        # 6. Если назначение — существующий каталог, кладём туда с тем же именем
        if os.path.isdir(dst_abs) and not os.path.islink(dst_abs):
            final_dst = os.path.join(dst_abs, os.path.basename(src_abs))
        else:
            final_dst = dst_abs

        # 7. Не перезаписываем существующие файлы
        if os.path.exists(final_dst) or os.path.islink(final_dst):
            return (f"mv: отказ — назначение уже существует:\n"
                    f"    {final_dst}\n"
                    f"mv: перезапись запрещена. Укажите другое имя или удалите цель")

        # 8. Родитель назначения должен существовать
        dst_parent = os.path.dirname(final_dst)
        if not os.path.isdir(dst_parent):
            return (f"mv: не удаётся переместить в '{dst_arg}': "
                    f"Нет такого каталога: {dst_parent}")

        # 9. Симлинк источника, ведущий наружу, запрещён
        src_real = os.path.realpath(src_abs)
        if src_real != src_abs and not os.path.islink(src_abs):
            return (f"mv: отказ — источник содержит симлинк наружу:\n"
                    f"    {src_abs} -> {src_real}")

        # 10. Перемещение
        try:
            os.rename(src_abs, final_dst)
            if os.path.isdir(dst_abs) and not os.path.islink(dst_abs) and dst_abs != final_dst:
                return f"mv: '{src_arg}' -> '{os.path.relpath(final_dst, cwd_real)}'"
            return f"mv: перемещено: {src_arg} -> {dst_arg}"
        except OSError as e:
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