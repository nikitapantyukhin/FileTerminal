import json
import shutil
import os
import stat
import time
from pathlib import Path


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
    for i in range(max_retries):
        try:
            if path.is_file():
                path.unlink()
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
    """Отмена последней команды (cp, mv, rm)"""
    undo_file = Path('.undo')  # Изменено на .undo

    if not undo_file.exists():
        return False, ["Никаких операций для отмены"], False

    try:
        with open(undo_file, 'r', encoding='utf-8') as f:
            operations = json.load(f)

        if not operations:
            return False, ["Никаких операций для отмены"], False

        last_op = operations[-1]
        op_type = last_op.get('type')

        if op_type == 'cp':
            source = Path(last_op['source'])
            destination = Path(last_op['destination'])

            if destination.exists():
                if source.is_dir() and destination.is_dir():
                    copied_item = destination / source.name
                    if copied_item.exists():
                        try:
                            safe_remove(str(copied_item))
                            result_message = f"Отменить cp: удалено {copied_item}"
                        except Exception as e:
                            return False, [f"ОШИБКА: Не удалось удалить {copied_item}: {e}"], False
                    else:
                        result_message = f"Предупреждение: {copied_item} не существует"
                elif source.is_file() and destination.is_dir():
                    copied_item = destination / source.name
                    if copied_item.exists():
                        try:
                            safe_remove(str(copied_item))
                            result_message = f"Отменить cp: удалено {copied_item}"

                        except Exception as e:
                            return False, [f"ОШИБКА: Не удалось удалить {copied_item}: {e}"], False
                    else:
                        result_message = f"Предупреждение: {copied_item} не существует"
                else:
                    try:
                        safe_remove(str(destination))
                        result_message = f"Отменить cp: удалено {destination}"
                    except Exception as e:
                        return False, [f"ОШИБКА: Не удалось удалить {destination}: {e}"], False
            else:
                result_message = f"Предупреждение: {destination} не существует"

        elif op_type == 'mv':
            source = Path(last_op['source'])
            destination = Path(last_op['destination'])
            moved_item = Path(last_op.get('moved_item', destination))

            if moved_item.exists():
                try:
                    if source.exists():
                        backup_path = source.with_name(f"{source.name}.backup")
                        if backup_path.exists():
                            safe_remove(str(backup_path))
                        shutil.move(str(source), str(backup_path))
                        result_message = f"Undo mv: moved {moved_item} back to {source} (original backed up as {backup_path})"
                    else:
                        result_message = f"Undo mv: moved {moved_item} back to {source}"

                    shutil.move(str(moved_item), str(source))

                except Exception as e:
                    return False, [f"ERROR: Failed to move {moved_item} back to {source}: {e}"], False
            else:
                result_message = f"Предупреждение: {moved_item} не существует"

        elif op_type == 'rm':
            original_path = Path(last_op['original_path'])
            trash_path = Path(last_op['trash_path'])

            if trash_path.exists():
                try:
                    original_path.parent.mkdir(parents=True, exist_ok=True)

                    if original_path.exists():
                        backup_path = original_path.with_name(f"{original_path.name}.backup")
                        if backup_path.exists():
                            safe_remove(str(backup_path))
                        shutil.move(str(original_path), str(backup_path))
                        result_message = f"Undo rm: restored {original_path} (existing file backed up as {backup_path})"
                    else:
                        result_message = f"Undo rm: restored {original_path}"

                    shutil.move(str(trash_path), str(original_path))

                except Exception as e:
                    return False, [f"ОШИБКА: Не удалось восстановить {original_path}: {e}"], False
            else:
                result_message = f"Предупреждение: {trash_path} не существует в корзине"

        else:
            return False, [f"ОШИБКА: Неизвестный тип операции: {op_type}"], False

        operations.pop()
        with open(undo_file, 'w', encoding='utf-8') as f:
            json.dump(operations, f)

        return True, [result_message], False

    except Exception as e:
        return False, [f"ОШИБКА: {e}"], False