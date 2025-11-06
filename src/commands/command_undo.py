import json
import shutil
import os
import stat
import time
from pathlib import Path
from src.state import get_undo_file, get_trash_dir


def remove_readonly(func, path, exc_info):
    """Обработчик ошибок для shutil.rmtree"""

    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)

    except Exception:
        time.sleep(0.1)
        try:
            func(path)
        except Exception as e:
            print(f"Предупреждение: Не удалось удалить {path}: {e}")


def safe_rmtree(path: str):
    """Безопасное удаление дерева файлов"""
    max_retries = 3
    for i in range(max_retries):
        try:
            shutil.rmtree(path, onerror=remove_readonly)
            break
        except Exception as e:
            if i == max_retries - 1:
                raise e
            time.sleep(0.1)


def safe_remove(path: str):
    """Безопасное удаление файла или директории"""
    max_retries = 3
    path_obj = Path(path)
    for i in range(max_retries):
        try:
            if path_obj.is_file():
                path_obj.unlink()
            else:
                safe_rmtree(path)
            break
        except PermissionError:
            if i == max_retries - 1:
                raise
            try:
                os.chmod(path, stat.S_IWRITE)
            except:
                pass
            time.sleep(0.1)


def command_undo(args):
    """Отмена последней команды (cp, mv, rm) с undo файлом"""

    undo_file = get_undo_file()
    trash_dir = get_trash_dir()

    if not undo_file.exists():
        return False, ["Нет операций для отмены"], False

    try:
        with open(undo_file, 'r', encoding='utf-8') as f:
            operations = json.load(f)

        if not operations:
            return False, ["Нет операций для отмены"], False

        last_undoable_op = None
        for i in range(len(operations) - 1, -1, -1):
            op = operations[i]
            if op.get('type') in ['cp', 'mv', 'rm']:
                last_undoable_op = op
                operations.pop(i)
                break

        if not last_undoable_op:
            return False, ["Нет операций для отмены (cp, mv, rm)"], False

        op_type = last_undoable_op.get('type')
        result_message = ""

        if op_type == 'cp':
            destination = Path(last_undoable_op['destination'])
            if destination.exists():
                try:
                    safe_remove(str(destination))
                    result_message = f"Отменено cp: удалено {destination}"
                except Exception as e:
                    return False, [f"ОШИБКА: Не удалось удалить {destination}: {e}"], False
            else:
                result_message = f"Предупреждение: {destination} не существует"

        elif op_type == 'mv':
            source = Path(last_undoable_op['source'])
            moved_item = Path(last_undoable_op.get('moved_item', last_undoable_op['destination']))

            if moved_item.exists():
                try:
                    if source.exists():
                        backup_path = source.with_name(f"{source.name}.backup")
                        if backup_path.exists():
                            safe_remove(str(backup_path))
                        shutil.move(str(source), str(backup_path))
                        result_message = f"Отменено mv: перемещено {moved_item} обратно в {source} (оригинал сохранен как {backup_path})"
                    else:
                        result_message = f"Отменено mv: перемещено {moved_item} обратно в {source}"

                    shutil.move(str(moved_item), str(source))
                except Exception as e:
                    return False, [f"ОШИБКА: Не удалось переместить {moved_item} обратно в {source}: {e}"], False
            else:
                result_message = f"Предупреждение: {moved_item} не существует"

        elif op_type == 'rm':
            original_path = Path(last_undoable_op['original_path'])
            trash_path = Path(last_undoable_op['trash_path'])

            if trash_path.exists():
                try:
                    original_path.parent.mkdir(parents=True, exist_ok=True)

                    if original_path.exists():
                        backup_path = original_path.with_name(f"{original_path.name}.backup")
                        if backup_path.exists():
                            safe_remove(str(backup_path))
                        shutil.move(str(original_path), str(backup_path))
                        result_message = f"Отменено rm: восстановлено {original_path} (существующий файл сохранен как {backup_path})"
                    else:
                        result_message = f"Отменено rm: восстановлено {original_path}"

                    shutil.move(str(trash_path), str(original_path))
                except Exception as e:
                    return False, [f"ОШИБКА: Не удалось восстановить {original_path}: {e}"], False
            else:
                result_message = f"Предупреждение: {trash_path} не существует в корзине"

        else:
            return False, [f"ОШИБКА: Неизвестный тип операции: {op_type}"], False

        with open(undo_file, 'w', encoding='utf-8') as f:
            json.dump(operations, f)

        return True, [result_message], False

    except Exception as e:
        return False, [f"ОШИБКА: {e}"], False