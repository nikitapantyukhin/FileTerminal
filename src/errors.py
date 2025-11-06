from colorama import Fore, Style


class TerminalError(Exception):
    """Класс всех ошибок мини-терминала"""
    def __init__(self, message):
        # Добавляем красный цвет к сообщению с помощью colorama
        super().__init__(f"{Fore.RED}{message}{Style.RESET_ALL}")


class ErrorNoCommand(TerminalError):
    """Отсутствие команды"""
    def __init__(self):
        super().__init__("Данная команда отсутствует!")


class ErrorLackOfLineSplitting(TerminalError):
    """Невозможность разбить строку на токены"""
    def __init__(self):
        super().__init__("Неправильная команда!")


class IncorrectNumberOfArgumentsForTheCommand(TerminalError):
    """Недостаток или избыток аргументов для команды"""
    def __init__(self, text):
        super().__init__(text)


class ErrorIsUnclosedParenthesesInArguments(TerminalError):
    """Незакрытые скобки в аргументах команды"""
    def __init__(self, text):
        super().__init__(text)


class ErrorIncorrectFlags(TerminalError):
    """Неправильно написанные флаги в команде"""
    def __init__(self):
        super().__init__("Флаг для команды написан неправильно")


class ErrorNoFileOrDirectory(TerminalError):
    """Несуществующий файл или директория"""
    def __init__(self, text):
        super().__init__(f"Ошибка. {text}: такого файла или директории не существует")


class ErrorIncorrectFileOrDirectoryName(TerminalError):
    """Неправильное название файла или директории"""
    def __init__(self):
        super().__init__("Неправильное название файла или директории")


class ErrorNotDirectory(TerminalError):
    def __init__(self, path):
        super().__init__(f"Ошибка. {path} это не директория")


class ErrorIsDirectory(TerminalError):
    def __init__(self, path):
        super().__init__(f"Ошибка. {path} это директория")


class ErrorPermissionDenied(TerminalError):
    def __init__(self, path):
        super().__init__(f"Ошибка. {path}: доступ запрещен")