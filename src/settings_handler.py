import json
import os
import random

# Generate random WiFi name only once at import time
RANDOM_SUFFIX = random.randint(1000, 9999)

# Default settings
DEFAULT_SETTINGS = {
    "servo1": {"on": 0, "off": 90},
    "reverse_steering": False,
    "reverse_motors": False,
    "toggle_weapon": False,
    "wifi": {
        "ap_name": f"Robot-{RANDOM_SUFFIX}",
        "ap_pass": "",  # Empty password is optional
    },
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
                        # For WiFi settings, preserve existing WiFi config values
                        if "wifi" not in settings:
                            settings["wifi"] = {}
                        
                        # Only set ap_name if it's not already set
                        if "ap_name" not in settings["wifi"]:
                            settings["wifi"]["ap_name"] = DEFAULT_SETTINGS["wifi"]["ap_name"]
                        
                        # Only set ap_pass if it's not already set
                        if "ap_pass" not in settings["wifi"]:
                            settings["wifi"]["ap_pass"] = DEFAULT_SETTINGS["wifi"]["ap_pass"]
                    else:
                        settings[key] = DEFAULT_SETTINGS[key]
            return settings
    except (OSError, ValueError):
        # File doesn't exist or is invalid, create and save default settings
        save_settings(DEFAULT_SETTINGS)
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
