from pathlib import Path
import os


def get_wsl_home_dir():
    """Определяет домашнюю директорию WSL"""
    home = os.environ.get('HOME')
    if home and Path(home).exists():
        return Path(home)

    username = os.environ.get('USER')
    if username:
        wsl_home = Path(f'/home/{username}')
        if wsl_home.exists():
            return wsl_home

    return Path('/home')


_home_dir = get_wsl_home_dir()


def find_project_root():
    """Находит корневую директорию проекта"""
    current = Path.cwd()

    for _ in range(5):
        if (current / 'src').exists() and (current / 'tests').exists():
            return current
        if current.parent == current:
            break
        current = current.parent

    return _home_dir


_project_root = find_project_root()

_current_path = Path.cwd() # Начальная директория

_history_file = _project_root / '.history'
_undo_file = _project_root / '.undo'
_trash_dir = _project_root / '.trash'

if not _trash_dir.exists():
    _trash_dir.mkdir(exist_ok=True)


def get_current_path():
    return _current_path


def set_current_path(new_path):
    global _current_path
    _current_path = Path(new_path).resolve()


def get_home_dir():
    return _home_dir


def get_history_file():
    return _history_file


def get_undo_file():
    return _undo_file


def get_trash_dir():
    return _trash_dir


def get_project_root():
    return _project_root
