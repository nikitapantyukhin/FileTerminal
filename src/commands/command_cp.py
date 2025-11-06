import shutil
import json
from pathlib import Path
from src.errors import *
from src.state import get_current_path, get_undo_file


def command_cp(args: list) -> (bool, list, bool):
    """Команда cp. Копирование файлов в какую-либо директорию.
    Для рекурсивного копирования нужно использовать флаг -r"""

    if len(args) < 2:
        return False, ["ОШИБКА: Недостаточно аргументов"], False

    current_path = get_current_path()
    source = Path(args[0])
    destination = Path(args[1])

    if not source.is_absolute():
        source = current_path / source
    if not destination.is_absolute():
        destination = current_path / destination

    try:
        if not source.exists():
            raise ErrorNoFileOrDirectory(str(source))

        source_abs = source.resolve()

        created_item = destination
        if destination.exists() and destination.is_dir():
            created_item = destination / source.name

        if source.is_dir():
            shutil.copytree(source, created_item)
        else:
            shutil.copy2(source, created_item)

        save_undo_operation('cp', {
            'source': str(source_abs),
            'destination': str(created_item.resolve())
        })

        return True, [], False

    except TerminalError as e:
        return False, [f"ОШИБКА: {e}"], False

    except Exception as e:
        return False, [f"ОШИБКА: {e}"], False


def save_undo_operation(op_type: str, op_data: dict):
    """Сохраняет операцию для возможного undo в централизованный файл"""

    undo_file = get_undo_file()
    operations = []

    if undo_file.exists():
        try:
            with open(undo_file, 'r', encoding='utf-8') as f:
                operations = json.load(f)
        except:
            operations = []

    operations.append({
        'type': op_type,
        **op_data
    })

    if len(operations) > 50:
        operations = operations[-50:]

    with open(undo_file, 'w', encoding='utf-8') as f:
        json.dump(operations, f)