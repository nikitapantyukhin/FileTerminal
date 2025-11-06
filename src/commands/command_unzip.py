import zipfile
from pathlib import Path
from src.errors import *
from src.state import get_current_path

def command_unzip(args: list) -> (bool, list, bool):
    """Команда unzip. Распаковка ZIP архива"""

    if len(args) != 1:
        return False, ["ОШИБКА: для распаковки требуется ровно 1 аргумент: имя архива"], False

    archive_name = args[0]
    current_path = get_current_path()

    try:
        if Path(archive_name).is_absolute():
            archive_path = Path(archive_name)
        else:
            archive_path = current_path / archive_name

        if not archive_path.exists():
            raise ErrorNoFileOrDirectory(archive_name)

        with zipfile.ZipFile(archive_path, 'r') as zipf:
            zipf.extractall(current_path)  # Распаковываем в текущую директорию

        return True, [f"Извлеченный архив: {archive_name}"], False
    except TerminalError as e:
        return False, [f"ОШИБКА: {e}"], False
    except Exception as e:
        return False, [f"ОШИБКА: {e}"], False