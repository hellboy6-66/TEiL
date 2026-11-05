"""
Каталог команд TEiL и исполнитель безопасных команд.

Каждая команда описана словарём:
    name             — имя (без флагов)
    desc             — подсказка
    flags            — список галочек; однобуквенные (-a, -l, …)
                       склеиваются в один флаг вроде -al,
                       многословные (aux, -c 2, -h now) — отдельно
    arg_placeholder  — подсказка для поля аргумента
    instant          — если True, выполняется без диалога
    dangerous        — если True, реально НЕ выполняется
    sim              — lambda(cmd) -> str, текст «вывода» для опасных
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
        {"name": "top", "desc": "Снимок top",
         "flags": ["-bn1"]},
    ],

    "Система": [
        {"name": "uname", "desc": "Информация о ядре",
         "flags": ["-a", "-r", "-s"]},
        {"name": "lscpu", "desc": "Информация о CPU", "instant": True},
    ],

    "⚠ Опасные": [
        {
            "name": "rm", "desc": "Удаление файлов/каталогов",
            "flags": ["-r", "-f"],
            "arg_placeholder": "цель (например /)",
            "dangerous": True,
            "sim": lambda cmd: (
                f"[СИМУЛЯЦИЯ] {cmd}\n"
                "rm: рекурсивное удаление указанной цели\n"
                "rm: удалено 138 402 файла\n"
                "rm: освобождено 47.8 GB\n"
                "[!] Команда заблокирована TEiL. Реальная система не пострадала."
            ),
        },
        {
            "name": "dd", "desc": "Запись на устройство",
            "arg_placeholder": "if=/dev/zero of=/dev/sda",
            "dangerous": True,
            "sim": lambda cmd: (
                f"[СИМУЛЯЦИЯ] {cmd}\n"
                "1048576+0 записей получено\n"
                "1048576+0 записей отправлено\n"
                "5368709120 байт (5.4 GB) скопировано, 12.1 s, 443 MB/s\n"
                "[!] Устройство было бы полностью уничтожено. TEiL заблокировал команду."
            ),
        },
        {
            "name": "mkfs.ext4", "desc": "Форматирование раздела",
            "arg_placeholder": "устройство (например /dev/sda1)",
            "dangerous": True,
            "sim": lambda cmd: (
                f"[СИМУЛЯЦИЯ] {cmd}\n"
                "mke2fs 1.47.0\n"
                "Создание файловой системы ext4 ...\n"
                "Суперблок создан, inode-таблица создана.\n"
                "[!] Раздел был бы отформатирован. Команда заблокирована TEiL."
            ),
        },
        {
            "name": ":(){ :|:& };:", "desc": "Fork-бомба",
            "dangerous": True,
            "sim": lambda cmd: (
                f"[СИМУЛЯЦИЯ] {cmd}\n"
                "bash: fork: retry: Resource temporarily unavailable\n"
                "... (процесс продолжает плодить потомков)\n"
                "[!] Система «зависла бы». TEiL заблокировал команду."
            ),
        },
        {
            "name": "chmod", "desc": "Изменение прав",
            "flags": ["-R"],
            "arg_placeholder": "права цель (например 000 /)",
            "dangerous": True,
            "sim": lambda cmd: (
                f"[СИМУЛЯЦИЯ] {cmd}\n"
                "chmod: изменение прав на 141 203 объекта...\n"
                "[!] Команда заблокирована TEiL."
            ),
        },
        {
            "name": "shutdown", "desc": "Выключение/перезагрузка",
            "flags": ["-h now", "-r now"],
            "dangerous": True,
            "sim": lambda cmd: (
                f"[СИМУЛЯЦИЯ] {cmd}\n"
                "Broadcast message: The system is going down NOW!\n"
                "Stopping services... unmounting filesystems...\n"
                "[!] Компьютер был бы выключен. TEiL заблокировал команду."
            ),
        },
    ],
}


class CommandExecutor:
    """Выполняет безопасные команды и следит за текущей директорией."""

    TIMEOUT = 10

    def __init__(self, start_dir: str | None = None):
        self.cwd = start_dir or os.path.expanduser("~")

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

    def change_dir(self, path: str) -> tuple[bool, str]:
        path = os.path.expanduser(path.strip())
        new = path if os.path.isabs(path) else os.path.join(self.cwd, path)
        new = os.path.normpath(new)
        if os.path.isdir(new):
            self.cwd = new
            return True, ""
        return False, f"cd: нет такого каталога: {path}"