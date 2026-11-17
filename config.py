"""Управление настройками и историей TEiL."""

import os
import json

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "teili_config.json")

def load_settings() -> dict:
    """Загружает настройки. Возвращает словарь с дефолтными значениями, если файла нет."""
    defaults = {
        "is_light_theme": False,
        "cwd": os.path.expanduser("~"),
        "history": [],
        "max_history": 100
    }
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Обновляем дефолтные значения тем, что есть в файле
                defaults.update(data)
                return defaults
        except Exception:
            pass
            
    return defaults

def save_settings(is_light: bool, cwd: str, history: list, max_history: int):
    """Сохраняет настройки в JSON-файл."""
    data = {
        "is_light_theme": is_light,
        "cwd": cwd,
        "history": history,
        "max_history": max_history
    }
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Не удалось сохранить настройки: {e}")