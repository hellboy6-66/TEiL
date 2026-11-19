"""Управление настройками и историей TEiL."""

import os
import json

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "teil_config.json")

def load_settings() -> dict:
    defaults = {
        "is_light_theme": False,
        "cwd": os.path.expanduser("~"),
        "history": [],
        "max_history": 100,
        "lesson_idx": 0  
    }
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                defaults.update(data)
                return defaults
        except Exception:
            pass
            
    return defaults

def save_settings(is_light: bool, cwd: str, history: list, max_history: int, lesson_idx: int):
    data = {
        "is_light_theme": is_light,
        "cwd": cwd,
        "history": history,
        "max_history": max_history,
        "lesson_idx": lesson_idx
    }
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Не удалось сохранить настройки: {e}")