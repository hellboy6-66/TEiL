"""Данные и логика для интерактивных уроков TEiL."""

import os

LESSONS = [
    {
        "title": "Шаг 1: Создание папки",
        "desc": "Создайте папку с именем practice.\nВведите в терминале или выберите в меню: mkdir practice",
        "check": lambda cwd, cmd: os.path.isdir(os.path.join(cwd, "practice"))
    },
    {
        "title": "Шаг 2: Переход в папку",
        "desc": "Перейдите в созданную папку, чтобы работать внутри неё.\nВведите: cd practice",
        "check": lambda cwd, cmd: "practice" in cwd.split(os.sep)
    },
    {
        "title": "Шаг 3: Создание пустого файла",
        "desc": "Создайте пустой текстовый файл внутри папки.\nВведите: touch note.txt",
        "check": lambda cwd, cmd: os.path.isfile(os.path.join(cwd, "note.txt"))
    },
    {
        "title": "Шаг 4: Просмотр файлов",
        "desc": "Посмотрите список файлов в текущей папке.\nВведите: ls",
        "check": lambda cwd, cmd: "ls" in cmd.strip()
    },

    {
        "title": "Шаг 5: Запись текста в файл",
        "desc": "Создайте файл с текстом, используя перенаправление вывода.\nВведите: echo 'Hello TEiL' > hello.txt",
        "check": lambda cwd, cmd: os.path.isfile(os.path.join(cwd, "hello.txt"))
    },
    {
        "title": "Шаг 6: Чтение файла",
        "desc": "Прочитайте содержимое созданного файла.\nВведите: cat hello.txt",
        "check": lambda cwd, cmd: "cat" in cmd and "hello.txt" in cmd
    },
    {
        "title": "Шаг 7: Копирование файла",
        "desc": "Сделайте резервную копию вашего файла.\nВведите: cp hello.txt copy.txt",
        "check": lambda cwd, cmd: os.path.isfile(os.path.join(cwd, "copy.txt"))
    },
    {
        "title": "Шаг 8: Переименование файла",
        "desc": "Переименуйте резервную копию с помощью команды перемещения.\nВведите: mv copy.txt backup.txt",
        "check": lambda cwd, cmd: os.path.isfile(os.path.join(cwd, "backup.txt")) and not os.path.exists(os.path.join(cwd, "copy.txt"))
    },

    {
        "title": "Шаг 9: Подсчет слов",
        "desc": "Узнайте, сколько строк и слов в вашем файле.\nВведите: wc hello.txt",
        "check": lambda cwd, cmd: "wc" in cmd and "hello.txt" in cmd
    },
    {
        "title": "Шаг 10: Поиск программы",
        "desc": "Узнайте, где физически находится программа ls.\nВведите: which ls",
        "check": lambda cwd, cmd: "which" in cmd and "ls" in cmd
    },
    {
        "title": "Шаг 11: Время работы системы",
        "desc": "Посмотрите, как давно включен ваш компьютер.\nВведите: uptime",
        "check": lambda cwd, cmd: "uptime" in cmd
    },

    {
        "title": "Шаг 12: Удаление файлов",
        "desc": "Очистите папку: удалите note.txt, hello.txt и backup.txt.\nВведите: rm note.txt (и подтвердите), затем повторите для остальных файлов.",
        "check": lambda cwd, cmd: not os.path.exists(os.path.join(cwd, "note.txt")) 
                                  and not os.path.exists(os.path.join(cwd, "hello.txt")) 
                                  and not os.path.exists(os.path.join(cwd, "backup.txt"))
    }
]