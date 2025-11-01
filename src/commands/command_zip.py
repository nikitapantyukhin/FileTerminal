import zipfile
from pathlib import Path
from src.errors import *


def command_zip(args):
    """Создание ZIP архива из каталога"""
    if len(args) != 2:
        return False, ["ОШИБКА: для zip-файла требуется ровно 2 аргумента: имя папки и архива"], False

    folder, archive_name = args

    try:
        folder_path = Path(folder)
        archive_path = Path(archive_name)

        if not folder_path.exists():
            raise ErrorNoFileOrDirectory(folder)
        if not folder_path.is_dir():
            raise ErrorNotDirectory(folder)

        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in folder_path.rglob('*'):
                if file_path.is_file():
                    arch_name = file_path.relative_to(folder_path)
                    zipf.write(file_path, arch_name)

        return True, [f"Созданный архив: {archive_name}"], False
    except TerminalError as e:
        return False, [f"ОШИБКА: {e}"], False
    except Exception as e:
        return False, [f"ОШИБКА: {e}"], False