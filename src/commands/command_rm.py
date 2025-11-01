import shutil
from pathlib import Path
from src.errors import *

from src.commands.command_cp import save_undo_operation


def command_rm(args: str) -> (bool, list, bool):
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

    for path in paths_to_delete:
        try:
            target = Path(path).resolve()
            current_dir = Path.cwd().resolve()

            if not target.exists():
                raise ErrorNoFileOrDirectory(str(target))

            if current_dir.is_relative_to(target):
                return False, [f"ОШИБКА: Не удается удалить родительский каталог"], False

            if target.is_dir():
                if not recursive:
                    return False, [
                        f"ОШИБКА: {path} это директория (используйте -r для рекурсивного удаления)"], False

                if not force:
                    confirmation = input(f"Вы уверены, что хотите рекурсивно удалить каталог '{path}'? [Y/N]: ")
                    if confirmation.lower() != 'y':
                        return False, [f"Удаление отменено"], False

                trash_dir = Path('.trash')  # Изменено на .trash
                trash_dir.mkdir(exist_ok=True)

                base_name = target.name
                counter = 1
                trash_path = trash_dir / base_name
                while trash_path.exists():
                    trash_path = trash_dir / f"{base_name}_{counter}"
                    counter += 1

                save_undo_operation('rm', {
                    'original_path': str(target.resolve()),
                    'trash_path': str(trash_path)
                })

                shutil.move(str(target), str(trash_path))
            else:
                trash_dir = Path('.trash')  # Изменено на .trash
                trash_dir.mkdir(exist_ok=True)

                base_name = target.name
                counter = 1
                trash_path = trash_dir / base_name
                while trash_path.exists():
                    name_parts = base_name.split('.')
                    if len(name_parts) > 1:
                        name = '.'.join(name_parts[:-1])
                        ext = name_parts[-1]
                        trash_path = trash_dir / f"{name}_{counter}.{ext}"
                    else:
                        trash_path = trash_dir / f"{base_name}_{counter}"
                    counter += 1

                save_undo_operation('rm', {
                    'original_path': str(target.resolve()),
                    'trash_path': str(trash_path)
                })

                shutil.move(str(target), str(trash_path))

        except TerminalError as e:
            return False, [str(e)], False

        except Exception as e:
            return False, [f"ERROR: {e}"], False

    return True, [], False