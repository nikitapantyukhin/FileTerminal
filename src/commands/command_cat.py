from pathlib import Path

from src.errors import *
from src.state import get_current_path


def command_cat(args: list) -> (bool, list, bool):
    """Команда cat. Вывод содержимого файлов args.
    При отсутствии или если аргумент будет директорией - ошибка"""

    if not args:
        return False, ["Ошибка: отсутствуют аргументы"], False

    current_path = get_current_path()
    results = []

    for path in args:
        try:
            if Path(path).is_absolute():
                file_path = Path(path)
            else:
                file_path = current_path / path

            if not file_path.exists():
                raise ErrorNoFileOrDirectory(path)
            if file_path.is_dir():
                raise ErrorIsDirectory(path)

            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                results.append(content)

        except TerminalError as e:
            results.append(str(e))

        except Exception as e:
            results.append(f"Ошибка: {e}")

    return True, results, True