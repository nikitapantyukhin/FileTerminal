import stat, time
from pathlib import Path

from src.errors import *


def command_ls(args: str) -> (bool, list, bool):
    current_dir = Path(".")

    is_args_in_input_command = False
    is_flag_l_in_args = False
    error_implementations = False

    if args:
        temp_args = args.copy()
        for arg in temp_args:
            if arg.startswith('-'):
                if all(char in '-l' for char in arg):
                    if 'l' in arg:
                        is_flag_l_in_args = True
                    args.remove(arg)
                else:
                    raise ErrorIncorrectFlags()

        if args:
            is_args_in_input_command = True

    list_result_args = []
    list_result_print = []
    cnt_args = False

    if is_args_in_input_command:
        for path in args:
            try:
                if is_flag_l_in_args:
                    list_result_args.append(processing_path_with_argument_with_flag(path))
                    error_implementations = True
                else:
                    list_result_args.append(processing_path_with_argument_without_flag(path) + '\n')
                    error_implementations = True
            except TerminalError as e:
                list_result_args.append(str(e))
            except Exception as e:
                list_result_args.append(f"Ошибка: {e}")

        list_result_print = correct_conclusion_for_more_than_one_argument(list_result_args, is_flag_l_in_args)

        cnt_args = True

    else:
        if is_flag_l_in_args:
            cnt_args = True
            result = []
            try:
                files = [p for p in current_dir.iterdir() if p.is_file()]
                dirs = [p for p in current_dir.iterdir() if p.is_dir()]

                for p in files:
                    result.append(output_of_full_information_about_argument_with_flag(p))
                for p in dirs:
                    result.append(output_of_full_information_about_argument_with_flag(p))

                list_result_print = result
            except Exception as e:
                list_result_print = [f"Ошибка: {e}"]
        else:
            items = [item.name for item in current_dir.iterdir()]
            list_result_print = [' '.join(items)]
            cnt_args = True

        error_implementations = True

    return error_implementations, list_result_print, cnt_args


def file_processing_without_flag(path: str) -> str:
    """Обработка если аргумент является файлом без флага l."""
    return path


def directory_processing_without_flag(path: str, arg) -> str:
    """Обработка если аргумент является директорией без флага l."""
    # Получаем имена элементов директории и объединяем в одну строку
    items = [item.name for item in arg.iterdir()]
    result_dir = ' '.join(items)

    return f"{path}:\n{result_dir}"


def processing_path_with_argument_without_flag(path: str):
    """Обработка аргумента в веденной команде без флага"""

    arg = Path(path)

    try:
        if not arg.exists():
            raise ErrorNoFileOrDirectory(arg)
    except ErrorNoFileOrDirectory as e:
        return str(e)

    if arg.is_file():
        return file_processing_without_flag(path)

    if arg.is_dir():
        return directory_processing_without_flag(path, arg)

    raise ErrorIncorrectFileOrDirectoryName()


def file_processing_with_flag(path):
    """Обработка если аргумент является файлом с флагом l."""

    file_path = Path(path)
    return output_of_full_information_about_argument_with_flag(file_path)


def directory_processing_with_flag(path: str, arg) -> str:
    """Обработка если аргумент является директорией с флагом l."""
    result_dir = []
    try:
        files = [p for p in arg.iterdir() if p.is_file()]
        dirs = [p for p in arg.iterdir() if p.is_dir()]

        for p in files:
            result_dir.append(output_of_full_information_about_argument_with_flag(p))
        for p in dirs:
            result_dir.append(output_of_full_information_about_argument_with_flag(p))

        return f"{path}:\n" + ''.join(result_dir)

    except Exception as e:

        return f"Ошибка при обработке директории {path}: {e}"


def processing_path_with_argument_with_flag(path):
    """Обработка аргумента в веденной команде с флагом -l"""
    arg = Path(path)

    try:
        if not arg.exists():
            raise ErrorNoFileOrDirectory(arg)
    except ErrorNoFileOrDirectory as e:
        return str(e)

    if arg.is_file():
        return file_processing_with_flag(path)

    if arg.is_dir():
        return directory_processing_with_flag(path, arg)

    raise ErrorIncorrectFileOrDirectoryName()


def getting_rights_for_argument(path):
    """Получение прав доступа к файлу в формате ls -l"""
    p = path.stat()

    permissions = ""

    # Тип файла
    if path.is_dir():
        permissions += "d"
    else:
        permissions += "-"

    # Права владельца
    permissions += "r" if p.st_mode & stat.S_IRUSR else "-"
    permissions += "w" if p.st_mode & stat.S_IWUSR else "-"
    permissions += "x" if p.st_mode & stat.S_IXUSR else "-"

    # Права группы
    permissions += "r" if p.st_mode & stat.S_IRGRP else "-"
    permissions += "w" if p.st_mode & stat.S_IWGRP else "-"
    permissions += "x" if p.st_mode & stat.S_IXGRP else "-"

    # Права остальных
    permissions += "r" if p.st_mode & stat.S_IROTH else "-"
    permissions += "w" if p.st_mode & stat.S_IWOTH else "-"
    permissions += "x" if p.st_mode & stat.S_IXOTH else "-"

    return permissions


def output_of_full_information_about_argument_with_flag(path):
    """Возвращение полной информации об аргументе"""
    try:
        p = path.stat()

        name = path.name  # Имя файла

        size = p.st_size  # Размер файла

        links = p.st_nlink  # Количество жестких ссылок

        permissions = getting_rights_for_argument(path)  # Права доступа

        m_time = time.strftime('%b %d %H:%M', time.localtime(p.st_mtime))  # Время последнего изменения

        return f"{permissions} {links:>2} {size:>8} {m_time} {name}\n"
    except Exception as e:
        return f"Ошибка при получении информации о {path}: {e}"


def correct_conclusion_for_more_than_one_argument(list_result_incorrect: list, is_flag: bool) -> list:
    """Вывод, если аргументов у команды больше 1"""
    list_errors = []
    list_files = []
    list_directory_items = []

    for item in list_result_incorrect:
        if item.startswith('Ошибка'):
            list_errors.append(item)
        else:
            if is_flag:
                list_files.append(item)
            else:
                path = Path(item)
                if path.exists() and path.is_file():
                    list_files.append(item)
                else:
                    list_directory_items.append(item)

    if is_flag:
        list_result_correct = list_errors + list_files + list_directory_items
    else:
        result = []

        result.extend(list_errors)

        if list_files:
            files_line = ' '.join(list_files)
            result.append(files_line)

        result.extend(list_directory_items)

        list_result_correct = result

    return list_result_correct