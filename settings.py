import json

# Default settings
settings = {
    "headless": False,
    "window_width": 1920,
    "window_height": 1080,
    "default_save_folder": ""
}

# Load regions data
with open("regions.json", "r", encoding="utf-8") as file:
    regions_dict = json.load(file)