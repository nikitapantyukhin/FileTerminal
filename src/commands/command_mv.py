import shutil
from pathlib import Path
from src.errors import *
from src.state import get_current_path
from src.commands.command_cp import save_undo_operation


def command_mv(args: list) -> (bool, list, bool):
    """Команда mv. Перемещение аргументов в директорию, которая должна быть написана последней.
    При отсутствии - ошибка."""

    if len(args) < 2:
        return False, ["ОШИБКА: Недостаточно аргументов"], False

    current_path = get_current_path()
    errors = []
    moved_files = []

    if len(args) > 2:
        destination = Path(args[-1])
        if not destination.is_absolute():
            destination = current_path / destination

        if not destination.exists():
            errors.append(f"mv: цель '{args[-1]}' не является директорией")
            return False, errors, True
        if not destination.is_dir():
            errors.append(f"mv: цель '{args[-1]}' не является директорией")
            return False, errors, True

        for source_path in args[:-1]:
            try:
                source = Path(source_path)
                if not source.is_absolute():
                    source = current_path / source

                if not source.exists():
                    errors.append(f"mv: невозможно переместить '{source_path}': Нет такого файла или директории")
                    continue

                final_destination = destination / source.name

                save_undo_operation('mv', {
                    'source': str(source.resolve()),
                    'destination': str(destination.resolve()),
                    'moved_item': str(final_destination.resolve())
                })

                shutil.move(str(source), str(destination))
                moved_files.append(source_path)

            except TerminalError as e:
                errors.append(str(e))

            except Exception as e:
                errors.append(f"mv: ошибка при перемещении '{source_path}': {e}")

    else:
        source = Path(args[0])
        destination = Path(args[1])

        if not source.is_absolute():
            source = current_path / source
        if not destination.is_absolute():
            destination = current_path / destination

        try:
            if not source.exists():
                errors.append(f"mv: невозможно переместить '{args[0]}': Нет такого файла или директории")
            else:
                source_abs = source.resolve()
                destination_abs = destination.resolve()

                moved_item = destination
                if destination.exists() and destination.is_dir():
                    moved_item = destination / source.name

                save_undo_operation('mv', {
                    'source': str(source_abs),
                    'destination': str(destination_abs),
                    'moved_item': str(moved_item.resolve())
                })

                shutil.move(str(source), str(destination))
                moved_files.append(args[0])

        except TerminalError as e:
            errors.append(str(e))
        except Exception as e:
            errors.append(f"mv: ошибка при перемещении '{args[0]}': {e}")

    result = []
    if moved_files:
        for moved in moved_files:
            result.append(f"перемещено '{moved}'")
    if errors:
        for error in errors:
            result.append(error)

    if moved_files:
        return True, result, True
    else:
        return False, result, True