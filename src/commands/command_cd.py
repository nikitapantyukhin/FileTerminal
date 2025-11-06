from src.errors import *
from src.state import get_current_path, set_current_path, get_home_dir

def command_cd(args: list) -> (bool, list, bool):
    """Команда cd. Переход в какую-либо директорию.
    При отсутствии директории - ошибка"""

    if not args:
        home_dir = get_home_dir()
        set_current_path(home_dir)
        return True, [], False

    path = args[0]

    try:
        if path == "~":
            new_path = get_home_dir()
        else:
            current_path = get_current_path()
            new_path = (current_path / path).resolve()

        if not new_path.exists():
            raise ErrorNoFileOrDirectory(path)
        if not new_path.is_dir():
            raise ErrorNotDirectory(path)

        set_current_path(new_path)
        return True, [], False

    except TerminalError as e:
        return False, [str(e)], False

    except Exception as e:
        return False, [f"Ошибка: {e}"], False