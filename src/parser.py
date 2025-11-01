import shlex
from src.errors import *


def parsing_and_checking_command(input_command: str) -> (str, list):
    """Основная функция, которая связывает парсинг введенной команды и делает проверку"""

    command, args = splitting_into_tokens(input_command)
    checking_for_the_correct_command(command, args)
    return command, args


def splitting_into_tokens(input_command: str) -> (str, list):
    """Парсинг введенной команды."""

    try:
        tokens = shlex.split(input_command)

        if not tokens:
            raise ErrorLackOfLineSplitting()

        command = tokens[0]
        arguments = tokens[1:]

        return command, arguments

    except Exception:
        raise ErrorLackOfLineSplitting()


def checking_for_the_correct_command(command: str, args: list) -> None:
    """Проверка на минимальное и максимальное возможное количество аргументов для команды."""

    dictionary_of_commands = {
        'ls': (0, None),
        'cd': (0, 1),
        'cat': (1, None),
        'cp': (2, None),
        'mv': (2, None),
        'rm': (1, None),
        'zip': (2, 2),
        'unzip': (1, 1),
        'tar': (2, 2),
        'untar': (1, 1),
        'grep': (2, None),
        'history': (0, 1),  # Изменено: теперь принимает 0 или 1 аргумент
        'undo': (0, 0)
    }

    if command not in dictionary_of_commands:
        raise ErrorNoCommand()

    cnt_args = len(args)
    min_args, max_args = dictionary_of_commands[command]

    if cnt_args < min_args:
        raise IncorrectNumberOfArgumentsForTheCommand(
            f"Для команды {command} требуется как минимум {min_args} аргументов. Вы указали {cnt_args}")

    if max_args is not None and cnt_args > max_args:
        raise IncorrectNumberOfArgumentsForTheCommand(
            f"Команда {command} принимает не более аргументов {max_args}. Вы указали аргументы {cnt_args}")