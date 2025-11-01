import os
from pathlib import Path
from src.errors import *


def command_cd(args: str) -> (bool, list, bool):
    if not args:
        home_dir = Path.home()
        try:
            os.chdir(home_dir)
            return True, [], False
        except Exception as e:
            return False, [f"Ошибка: {e}"], False

    path = args[0]

    try:
        new_path = Path(path)
        if not new_path.exists():
            raise ErrorNoFileOrDirectory(path)
        if not new_path.is_dir():
            raise ErrorNotDirectory(path)

        os.chdir(new_path)
        return True, [], False

    except TerminalError as e:
        return False, [str(e)], False

    except Exception as e:
        return False, [f"Ошибка: {e}"], False