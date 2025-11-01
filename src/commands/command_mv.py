import shutil
from pathlib import Path

from src.errors import *
from src.commands.command_cp import save_undo_operation


def command_mv(args: str) -> (bool, list, bool):
    if len(args) < 2:
        return False, ["ERROR: Not enough arguments"], False

    source = Path(args[0])
    destination = Path(args[1])

    try:
        if not source.exists():
            raise ErrorNoFileOrDirectory(str(source))

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
        return True, [], False

    except TerminalError as e:
        return False, [f"ERROR: {e}"], False

    except Exception as e:
        return False, [f"ERROR: {e}"], False