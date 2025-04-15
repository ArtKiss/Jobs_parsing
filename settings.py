import json
import os


# Значения по умолчанию
default_settings = {
    "headless": False,
    "window_width": 1920,
    "window_height": 1080,
    "default_save_folder": "",
    "theme": "dark"
}

settings_path = "user_settings.json"
# Загружаем настройки
def load_settings():
    if os.path.exists(settings_path):
        try:
            with open(settings_path, "r", encoding="utf-8") as file:
                loaded = json.load(file)
                # Обновляем только известные поля, если что-то отсутствует — дополняем
                return {**default_settings, **loaded}
        except Exception as e:
            print(f"Ошибка загрузки настроек: {e}")
    return default_settings.copy()

# Сохраняем настройки
def save_settings(updated_settings):
    try:
        with open(settings_path, "w", encoding="utf-8") as file:
            json.dump(updated_settings, file, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Ошибка сохранения настроек: {e}")

# Загружаем регионы
with open("regions.json", "r", encoding="utf-8") as file:
    regions_dict = json.load(file)

# Загруженные настройки в глобальную переменную
settings = load_settings()