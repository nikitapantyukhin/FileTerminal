import tarfile
from pathlib import Path

from src.errors import *


def command_tar(args: str) -> (bool, list, bool):
    """Создание TAR.GZ архива"""

    if len(args) != 2:
        return False, ["ОШИБКА: tar требует ровно 2 аргумента: имя папки и архива"], False

    folder, archive_name = args

    try:
        folder_path = Path(folder)
        archive_path = Path(archive_name)

        if not folder_path.exists():
            raise ErrorNoFileOrDirectory(folder)
        if not folder_path.is_dir():
            raise ErrorNotDirectory(folder)

        with tarfile.open(archive_path, 'w:gz') as tar:
            tar.add(folder_path, arcname=folder_path.name)

        return True, [f"Созданный tar-архив: {archive_name}"], False

    except TerminalError as e:
        return False, [f"ОШИБКА: {e}"], False

    except Exception as e:
        return False, [f"ОШИБКА: {e}"], False