import tarfile
from pathlib import Path
from src.errors import *
from src.state import get_current_path

def command_untar(args: list) -> (bool, list, bool):
    """Команда untar. Распаковка TAR.GZ архива"""

    if len(args) != 1:
        return False, ["ОШИБКА: для untar требуется ровно 1 аргумент: имя архива"], False

    archive_name = args[0]
    current_path = get_current_path()

    try:
        if Path(archive_name).is_absolute():
            archive_path = Path(archive_name)
        else:
            archive_path = current_path / archive_name

        if not archive_path.exists():
            raise ErrorNoFileOrDirectory(archive_name)

        with tarfile.open(archive_path, 'r:gz') as tar:
            tar.extractall(current_path)  # Распаковываем в текущую директорию

        return True, [f"Извлеченный архив tar: {archive_name}"], False
    except TerminalError as e:
        return False, [f"ОШИБКА: {e}"], False
    except Exception as e:
        return False, [f"ОШИБКА: {e}"], False