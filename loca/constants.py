# Project-wide constants for loca

from pathlib import Path
import sys


CURRENT_PROJECT_ROOT_KEY = "current_project_root"
# Cache and config filenames
FILE_CACHE_FILENAME = "file_cache.json"
SNIPPET_CACHE_FILENAME = "snippet_cache.json"
CONFIG_FILENAME = "loca.config.json"

VENV_PATH = Path(sys.prefix).resolve()
