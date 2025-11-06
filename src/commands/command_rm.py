import shutil
from pathlib import Path
from src.errors import *
from src.state import get_current_path, get_trash_dir
from src.commands.command_cp import save_undo_operation


def command_rm(args: list) -> (bool, list, bool):
    if not args:
        return False, ["ОШИБКА: Отсутствуют аргументы"], False

    force = False
    recursive = False
    paths_to_delete = []

    for arg in args:
        if arg == '-f' or arg == '--force':
            force = True
        elif arg == '-r' or arg == '-R' or arg == '--recursive':
            recursive = True
        else:
            paths_to_delete.append(arg)

    if not paths_to_delete:
        return False, ["ОШИБКА: Отсутствуют пути для удаления"], False

    errors = []
    deleted_files = []
    current_path = get_current_path()
    trash_dir = get_trash_dir()

    for path in paths_to_delete:
        try:
            if Path(path).is_absolute():
                target = Path(path)
            else:
                target = current_path / path

            target = target.resolve()

            if not target.exists():
                errors.append(f"rm: невозможно удалить '{path}': Нет такого файла или директории")
                continue

            if current_path == target or current_path.is_relative_to(target):
                errors.append(f"rm: невозможно удалить '{path}': Это текущая или родительская директория")
                continue

            if target.is_dir():
                if not recursive:
                    errors.append(
                        f"rm: невозможно удалить '{path}': Это директория (используйте -r для рекурсивного удаления)")
                    continue

                if not force:
                    confirmation = input(f"Вы уверены, что хотите рекурсивно удалить каталог '{path}'? [Y/N]: ")
                    if confirmation.lower() != 'y':
                        errors.append(f"rm: удаление отменено для '{path}'")
                        continue

            base_name = target.name
            counter = 1
            trash_path = trash_dir / base_name

            while trash_path.exists():
                if target.is_dir():
                    trash_path = trash_dir / f"{base_name}_{counter}"
                else:
                    name_parts = base_name.split('.')
                    if len(name_parts) > 1:
                        name = '.'.join(name_parts[:-1])
                        ext = name_parts[-1]
                        trash_path = trash_dir / f"{name}_{counter}.{ext}"
                    else:
                        trash_path = trash_dir / f"{base_name}_{counter}"
                counter += 1

            save_undo_operation('rm', {
                'original_path': str(target),
                'trash_path': str(trash_path)
            })

            shutil.move(str(target), str(trash_path))
            deleted_files.append(path)

        except TerminalError as e:
            errors.append(str(e))
        except Exception as e:
            errors.append(f"rm: ошибка при удалении '{path}': {e}")

    result = []
    if deleted_files:
        for deleted in deleted_files:
            result.append(f"удалено: '{deleted}'")
    if errors:
        for error in errors:
            result.append(error)

    if deleted_files:
        return True, result, True
    else:
        return False, result, True