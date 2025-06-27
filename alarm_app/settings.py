import os
import json

SETTINGS_PATH = os.path.expanduser("~/Desktop/alarm_app/config/settings.json")

DEFAULTS = {
    "font_size": "medium",  # small, medium, large
    "show_milliseconds": False
}

def load_settings():
    if not os.path.exists(SETTINGS_PATH):
        return DEFAULTS.copy()
    try:
        with open(SETTINGS_PATH, "r") as f:
            return json.load(f)
    except:
        return DEFAULTS.copy()

def save_settings(settings):
    try:
        with open(SETTINGS_PATH, "w") as f:
            json.dump(settings, f, indent=2)
    except Exception as e:
        print(f"[Settings Save Error] {e}")
