import json
from pathlib import Path
from typing import Any, Dict

from platformdirs import user_cache_dir
from .constants import CONFIG_FILENAME

CONFIG_FILE = Path(user_cache_dir("loca")) / CONFIG_FILENAME


def load_config() -> Dict[str, Any]:
    """
    Load configuration from a JSON file.
    Returns a dictionary with the configuration.
    """
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            # Config file does not exist, create an empty one
            json.dump({}, f, indent=4)
        return {}
    except json.JSONDecodeError:
        # Config file is corrupted, reset to empty
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=4)
        return {}


def add_to_config(key: str, value: Any) -> None:
    """
    Add a key-value pair to the configuration file.
    If the key already exists, it will be updated.
    """
    config = load_config()
    config[key] = value
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)
