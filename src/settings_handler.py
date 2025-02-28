import json
import os

# Default settings
DEFAULT_SETTINGS = {
    "servo1": {
        "on": 0,
        "off": 90
    },
    "reverse_steering": False,
    "reverse_motors": False,
    "toggle_weapon": False  # Added default toggle_weapon setting
}

SETTINGS_FILE = "settings.json"

def load_settings():
    """Load settings from file or return defaults if file doesn't exist"""
    try:
        with open(SETTINGS_FILE, "r") as f:
            settings = json.load(f)
            # Ensure all default settings exist
            for key in DEFAULT_SETTINGS:
                if key not in settings:
                    settings[key] = DEFAULT_SETTINGS[key]
            return settings
    except (OSError, ValueError):
        # File doesn't exist or is invalid, return defaults
        return DEFAULT_SETTINGS

def save_settings(settings):
    """Save settings to file"""
    # Ensure all default settings exist
    for key in DEFAULT_SETTINGS:
        if key not in settings:
            settings[key] = DEFAULT_SETTINGS[key]
    
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f)
    return True
