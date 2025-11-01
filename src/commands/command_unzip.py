import zipfile
from pathlib import Path
from src.errors import *


def command_unzip(args):
    """Распаковка ZIP архива"""
    if len(args) != 1:
        return False, ["ОШИБКА: для распаковки требуется ровно 1 аргумент: имя архива"], False

    archive_name = args[0]

    try:
        archive_path = Path(archive_name)

        if not archive_path.exists():
            raise ErrorNoFileOrDirectory(archive_name)

        with zipfile.ZipFile(archive_path, 'r') as zipf:
            zipf.extractall()

        return True, [f"Извлеченный архив: {archive_name}"], False
    except TerminalError as e:
        return False, [f"ОШИБКА: {e}"], False
    except Exception as e:
        return False, [f"ОШИБКА: {e}"], False