import datetime
from pathlib import Path
from src.state import get_project_root


def get_log_file_path():
    """Возвращает путь к файлу логов в корневой директории проекта"""
    project_root = get_project_root()
    log_file = project_root / 'shell.log'
    return log_file


def log_command(command_string: str, success: bool, error_message: str = None):
    """
    Логирует команду и результат её выполнения в файл shell.log в корне проекта
    """
    current_time = datetime.datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')
    log_file = get_log_file_path()

    try:
        with open(log_file, 'a', encoding='utf-8') as log_file_obj:
            log_file_obj.write(f"{current_time} {command_string}\n")

            if not success and error_message:
                log_file_obj.write(f"{current_time} ERROR: {error_message}\n")

    except Exception as e:
        print(f"Предупреждение: Не удалось выполнить запись в файл журнала: {e}")