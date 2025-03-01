import json
import os
import random

# Default settings
DEFAULT_SETTINGS = {
    "servo1": {
        "on": 0,
        "off": 90
    },
    "reverse_steering": False,
    "reverse_motors": False,
    "toggle_weapon": False,
    "wifi": {
        "ap_name": f"Robot-{random.randint(1000, 9999)}",
        "ap_pass": ""  # Empty password is optional
    }
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
                    if key == "wifi":
                        # For WiFi settings, we need to keep the random number consistent
                        settings[key] = DEFAULT_SETTINGS[key]
                    else:
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
