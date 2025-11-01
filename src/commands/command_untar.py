import tarfile
from pathlib import Path

from src.errors import *


def command_untar(args):
    """Распаковка TAR.GZ архива"""
    if len(args) != 1:
        return False, ["ОШИБКА: для untar требуется ровно 1 аргумент: имя архива"], False

    archive_name = args[0]

    try:
        archive_path = Path(archive_name)

        if not archive_path.exists():
            raise ErrorNoFileOrDirectory(archive_name)

        with tarfile.open(archive_path, 'r:gz') as tar:
            tar.extractall()

        return True, [f"Извлеченный архив tar: {archive_name}"], False
    except TerminalError as e:
        return False, [f"ОШИБКА: {e}"], False
    except Exception as e:
        return False, [f"ОШИБКА: {e}"], False