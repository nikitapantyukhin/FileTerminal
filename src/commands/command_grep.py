import re
from pathlib import Path

from src.errors import *


def command_grep(args):
    """Поиск строк в файлах по шаблону"""
    if len(args) < 2:
        return False, ["ОШИБКА: для grep требуется как минимум 2 аргумента: pattern и path"], False

    recursive = False
    ignore_case = False
    pattern_args = []

    i = 0
    while i < len(args):
        arg = args[i]
        if arg == '-r':
            recursive = True
        elif arg == '-i':
            ignore_case = True
        else:
            pattern_args.append(arg)
        i += 1

    if len(pattern_args) < 2:
        return False, ["ОШИБКА: для grep требуются аргументы pattern и path"], False

    pattern = pattern_args[0]
    search_path = pattern_args[1]

    try:
        path = Path(search_path)
        if not path.exists():
            raise ErrorNoFileOrDirectory(search_path)

        flags = re.IGNORECASE if ignore_case else 0
        regex = re.compile(pattern, flags)

        results = []

        if path.is_file():
            results.extend(search_in_file(path, regex))
        elif path.is_dir():
            if recursive:
                for file_path in path.rglob('*'):
                    if file_path.is_file():
                        results.extend(search_in_file(file_path, regex))
            else:
                for file_path in path.iterdir():
                    if file_path.is_file():
                        results.extend(search_in_file(file_path, regex))

        return True, results, True

    except TerminalError as e:
        return False, [f"ОШИБКА: {e}"], False

    except Exception as e:
        return False, [f"ОШИБКА: {e}"], False


def search_in_file(file_path, regex):
    """Поиск шаблона в одном файле"""
    results = []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            for line_num, line in enumerate(file, 1):
                if regex.search(line):
                    clean_line = line.strip()
                    results.append(f"{file_path}:{line_num}: {clean_line}")

    except Exception as e:
        results.append(f"ОШИБКА: Не удалось прочитать {file_path}: {e}")

    return results