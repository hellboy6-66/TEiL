"""Данные и логика для интерактивных уроков TEiL."""

import os

LESSONS = [
    {
        "title": "Шаг 1: Создание папки",
        "desc": "Создайте папку с именем practice.\nДля этого введите в терминале или выберите в меню: mkdir practice",
        "check": lambda cwd, cmd: os.path.isdir(os.path.join(cwd, "practice"))
    },
    {
        "title": "Шаг 2: Переход в папку",
        "desc": "Перейдите в созданную папку, чтобы работать внутри неё.\nВведите: cd practice",
        "check": lambda cwd, cmd: "practice" in cwd.split(os.sep)
    },
    {
        "title": "Шаг 3: Создание файла",
        "desc": "Создайте пустой текстовый файл внутри папки.\nВведите: touch note.txt",
        "check": lambda cwd, cmd: os.path.isfile(os.path.join(cwd, "note.txt"))
    },
    {
        "title": "Шаг 4: Просмотр файлов",
        "desc": "Посмотрите список файлов в текущей папке.\nВведите: ls",
        "check": lambda cwd, cmd: "ls" in cmd.strip()
    },
    {
        "title": "Шаг 5: Удаление файла",
        "desc": "Удалите созданный файл, чтобы очистить систему.\nВведите: rm note.txt (и подтвердите удаление)",
        "check": lambda cwd, cmd: not os.path.exists(os.path.join(cwd, "note.txt"))
    }
]