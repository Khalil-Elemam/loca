import hashlib
from pathlib import Path
from typing import Set

from platformdirs import user_cache_dir


from .config import load_config
from .constants import CURRENT_PROJECT_ROOT_KEY, VENV_PATH


def read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def starts_with_any(string: str, prefixes: Set[str]) -> bool:
    """
    Check if the string starts with any of the given prefixes.
    """
    return any(string.startswith(f"{prefix}:") for prefix in prefixes)


def find_venvs(path: Path) -> Set[Path]:
    """
    Find all virtual environments in the given path.
    """
    return {cfg.parent for cfg in path.rglob("pyvenv.cfg")}


def get_project_root() -> Path:
    config = load_config()
    cwd = Path.cwd().resolve()
    project_root = config.get(CURRENT_PROJECT_ROOT_KEY)
    project_root_path = Path(project_root).resolve() if project_root else None
    if not project_root_path or not cwd.is_relative_to(project_root_path):
        raise RuntimeError(
            "❌ Project root not set in configuration. Please set it using `loca set-root` command."
        )
    return project_root_path


def get_project_cache_path() -> Path:
    """
    Get the path to the project cache directory.
    """
    project_root = get_project_root()
    root_bytes = str(project_root.resolve()).encode("utf-8")
    project_hash = hashlib.sha1(root_bytes).hexdigest()[:10]
    return Path(user_cache_dir("loca")) / project_hash


def scan_python_files(path: Path) -> list[Path]:
    """
    Recursively find all Python files in the project, excluding venv.
    """
    return [
        f
        for f in path.rglob("*.py")
        if not (f.is_symlink() or f.resolve().is_relative_to(VENV_PATH))
    ]
