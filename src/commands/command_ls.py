import stat, time
from pathlib import Path

from src.errors import *
from src.state import get_current_path, get_home_dir


def command_ls(args: list) -> (bool, list, bool):
    """Команда ls. Вывод содержимого аргументов.
    Для подробного просмотра использовать флаг -l.
    В выводе при использовании флага -l
    будет сначала выводится ошибки(файлы или директории, которые не существуют),
    потом файлы, затем директории"""

    current_dir = get_current_path()

    is_args_in_input_command = False
    is_flag_l_in_args = False
    error_implementations = False

    hidden_files = ['.history', '.undo', '.shell.log', '.trash', '.pre-commit-config.yaml', '.gitignore', 'idea']

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

    if is_args_in_input_command:
        for path in args:
            try:
                full_path = current_dir / path
                if is_flag_l_in_args:
                    result = processing_path_with_argument_with_flag(full_path, path)
                    list_result_args.append(result)
                    error_implementations = True
                else:
                    result = processing_path_with_argument_without_flag(full_path, path)
                    list_result_args.append(result)
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
                files = [p for p in current_dir.iterdir() if p.is_file() and p.name not in hidden_files]
                dirs = [p for p in current_dir.iterdir() if p.is_dir() and p.name not in hidden_files]

                for p in files:
                    result.append(output_of_full_information_about_argument_with_flag(p))
                for p in dirs:
                    result.append(output_of_full_information_about_argument_with_flag(p))

                list_result_print = result
            except Exception as e:
                list_result_print = [f"Ошибка: {e}"]
        else:
            items = [item.name for item in current_dir.iterdir() if item.name not in hidden_files]
            colored_items = []
            for item in items:
                item_path = current_dir / item
                if item_path.is_dir():
                    colored_items.append(f"{Fore.BLUE}{item}{Style.RESET_ALL}")
                else:
                    colored_items.append(item)
            list_result_print = [' '.join(colored_items)]
            cnt_args = True

        error_implementations = True

    return error_implementations, list_result_print, cnt_args


def file_processing_without_flag(path: Path, display_name: str) -> str:
    """Обработка если аргумент является файлом без флага l."""

    return display_name


def directory_processing_without_flag(path: Path, display_name: str) -> str:
    """Обработка если аргумент является директорией без флага l."""

    hidden_files = ['.history', '.undo', '.shell.log', '.trash', '.pre-commit-config.yaml', '.gitignore', 'idea']
    items = [item.name for item in path.iterdir() if item.name not in hidden_files]

    colored_items = []
    for item in items:
        item_path = path / item
        if item_path.is_dir():
            colored_items.append(f"{Fore.BLUE}{item}{Style.RESET_ALL}")
        else:
            colored_items.append(item)

    result_dir = ' '.join(colored_items)
    return f"{Fore.BLUE}{display_name}:{Style.RESET_ALL}\n{result_dir}"


def processing_path_with_argument_without_flag(path: Path, display_name: str):
    """Обработка аргумента в веденной команде без флага"""

    try:
        if not path.exists():
            raise ErrorNoFileOrDirectory(display_name)
    except ErrorNoFileOrDirectory as e:
        return str(e)

    if path.is_file():
        return file_processing_without_flag(path, display_name)

    if path.is_dir():
        return directory_processing_without_flag(path, display_name)

    raise ErrorIncorrectFileOrDirectoryName()


def file_processing_with_flag(path: Path, display_name: str):
    """Обработка если аргумент является файлом с флагом l."""

    return output_of_full_information_about_argument_with_flag(path)


def directory_processing_with_flag(path: Path, display_name: str) -> str:
    """Обработка если аргумент является директорией с флагом l."""

    result_dir = []
    try:
        hidden_files = ['.history', '.undo', '.shell.log', '.trash', '.pre-commit-config.yaml', '.gitignore', 'idea']
        files = [p for p in path.iterdir() if p.is_file() and p.name not in hidden_files]
        dirs = [p for p in path.iterdir() if p.is_dir() and p.name not in hidden_files]

        for p in files:
            result_dir.append(output_of_full_information_about_argument_with_flag(p))
        for p in dirs:
            result_dir.append(output_of_full_information_about_argument_with_flag(p))

        if result_dir:
            return f"{Fore.BLUE}{display_name}:{Style.RESET_ALL}\n" + '\n'.join(result_dir)
        else:
            return f"{Fore.BLUE}{display_name}:{Style.RESET_ALL}\n"

    except Exception as e:
        return f"Ошибка при обработке директории {display_name}: {e}"


def processing_path_with_argument_with_flag(path: Path, display_name: str):
    """Обработка аргумента в веденной команде с флагом -l"""

    try:
        if not path.exists():
            raise ErrorNoFileOrDirectory(display_name)
    except ErrorNoFileOrDirectory as e:
        return str(e)

    if path.is_file():
        return file_processing_with_flag(path, display_name)

    if path.is_dir():
        return directory_processing_with_flag(path, display_name)

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

        return f"{permissions} {links:>2} {size:>8} {m_time} {name}"  # Убрали \n в конце
    except Exception as e:
        return f"Ошибка при получении информации о {path}: {e}"


def correct_conclusion_for_more_than_one_argument(list_result_incorrect: list, is_flag: bool) -> list:
    """Вывод, если аргументов у команды больше 1"""

    errors = []
    files = []
    directories = []

    for item in list_result_incorrect:
        if item.startswith('Ошибка') or item.startswith('ОШИБКА'):
            errors.append(item)
        else:
            lines = item.split('\n')
            first_line = lines[0]

            if first_line.endswith(':') and not first_line.startswith(('-', 'd', 'l')):
                directories.append(item)
            else:
                files.append(item)

    result = []

    if errors:
        result.extend(errors)
        if files or directories:
            result.append('')

    if files:
        if is_flag:
            result.extend(files)
        else:
            result.append(' '.join(files))

    if directories:
        if files:
            result.append('')

        for i, dir_item in enumerate(directories):
            lines = dir_item.split('\n')
            result.extend(lines)
            if i < len(directories) - 1:
                result.append('\n')

    return result