Руководство по установке TEiL (из исходного кода)
Данная инструкция предназначена для пользователей Linux, которые хотят запустить TEiL, используя исходный код на Python.

1. Установка системных зависимостей
Так как TEiL использует графический интерфейс на базе PyQt6, для его работы требуются системные библиотеки (особенно модуль xcb для отрисовки окон). Откройте терминал и выполните команды для вашего дистрибутива:

Для Ubuntu / Debian / Linux Mint / Pop!_OS:
    sudo apt update
    sudo apt install python3 python3-pip python3-venv git libxcb-cursor0 libxkbcommon-x11-0
Для Fedora / RHEL / AlmaLinux:
    sudo dnf install python3 python3-pip git xcb-util-cursor xcb-util-wm
Для Arch Linux / Manjaro / EndeavourOS:
    sudo pacman -S python python-pip git xcb-util-cursor
Для openSUSE:
    sudo zypper install python3 python3-pip git libxcb-cursor0

2. Клонирование репозитория
Скачайте исходный код проекта из GitHub. В терминале выполните:
bash

git clone https://github.com/hellboy6-66/TEiL.git
cd TEiL

3. Создание виртуального окружения (Рекомендуется)
Использование виртуального окружения (venv) — это правильная практика, которая не даст TEiL испортить системные пакеты Python.
Создайте окружение:
    python3 -m venv venv
Активируйте его:
    source venv/bin/activate
(В начале строки терминала появится префикс (venv), означающий, что вы внутри окружения).

4. Установка Python-зависимостей
Установите библиотеку PyQt6, которая необходима для работы приложения:
  pip install PyQt6

5. Запуск приложения
Убедитесь, что вы находитесь в папке с проектом, и запустите главный файл:

  python3 main.py

Если всё сделано правильно, откроется окно программы TEiL.

6. Частые проблемы и их решение

    Ошибка qt.qpa.plugin: Could not load the Qt platform plugin "xcb"
    Это самая популярная проблема в PyQt6 на Linux. Она означает, что не хватает системных библиотек. Вернитесь к пункту 1 и убедитесь, что вы установили пакеты libxcb-cursor0 (для Debian/Ubuntu) или xcb-util-cursor (для Arch/Fedora).

    Ошибка python3: command not found
    В некоторых системах Python может называться просто python. Попробуйте заменить в командах python3 на python.

    Не запускается скрипт activate
    Убедитесь, что вы находитесь в папке с проектом (где была создана папка venv), и используйте правильный путь: source venv/bin/activate.

7. Как удалить приложение
Если вы использовали виртуальное окружение, просто удалите папку с проектом:
bash

cd ..
rm -rf TEiL

Виртуальное окружение и все зависимости удалятся вместе с папкой, не оставив следов в системе.
