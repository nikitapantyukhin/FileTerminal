from pathlib import Path
from src.errors import *


def command_cat(arg: str) -> (bool, list, bool):
    """Функция, которая выводит содержимое файла arg
    Возвращает (bool, list, bool). """

    if not arg:
        return False, ["Ошибка: отсутствуют аргументы"], False

    results = []
    for path in arg:
        try:
            file_path = Path(path)
            if not file_path.exists():
                raise ErrorNoFileOrDirectory(path)
            if file_path.is_dir():
                raise ErrorIsDirectory(path)

            with open(file_path, 'r', encoding='utf-8') as file:
                c = file.read()
                results.append(c)

        except TerminalError as e:
            results.append(str(e))
        except Exception as e:
            results.append(f"Ошибка: {e}")

    return True, results, True