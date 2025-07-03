import json
import sys
from typing import Dict


from .utils import get_project_cache_path
from .constants import FILE_CACHE_FILENAME, SNIPPET_CACHE_FILENAME


def safe_cache_path(filename: str) -> str:
    """
    Get a cache path, handling project root errors with colorized output and exit.
    """
    try:
        return get_project_cache_path() / filename
    except RuntimeError as e:
        from colorama import Fore, Style

        print(f"{Fore.RED}{e}{Style.RESET_ALL}")
        sys.exit(1)


def get_file_cache() -> Dict[str, str]:
    """
    Returns a dictionary mapping file paths to their content.
    This is used to cache file content for quick access.
    """
    cache_path = safe_cache_path(FILE_CACHE_FILENAME)
    try:
        with open(cache_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        # Corrupted cache file, reset to empty
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=4)
        return {}


def get_snippet_cache() -> Dict[str, str]:
    """
    Returns a dictionary mapping snippet IDs to their content hash.
    This is used to cache snippet content for quick access.
    """
    cache_path = safe_cache_path(SNIPPET_CACHE_FILENAME)
    try:
        with open(cache_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        # Corrupted cache file, reset to empty
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=4)
        return {}


def save_file_cache(file_cache: Dict[str, str]) -> None:
    cache_path = safe_cache_path(FILE_CACHE_FILENAME)
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(file_cache, f, indent=4)


def save_snippet_cache(snippet_cache: Dict[str, str]) -> None:
    cache_path = safe_cache_path(SNIPPET_CACHE_FILENAME)
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(snippet_cache, f, indent=4)
