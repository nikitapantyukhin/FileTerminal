import datetime
from pathlib import Path


def get_log_file_path():
    """Возвращает путь к файлу логов в домашней директории пользователя"""
    home_dir = Path.home()
    log_file = home_dir / 'shell.log'
    return log_file


def log_command(command_string: str, success: bool, error_message: str = None):
    """
    Логирует команду и результат её выполнения в файл shell.log в домашней директории
    Формат: [дата/время] команда
    [дата/время] ERROR: сообщение_об_ошибке (если есть)
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