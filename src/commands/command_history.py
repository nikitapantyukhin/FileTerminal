from src.state import get_history_file


def command_history(args: list) -> (bool, list, bool):
    """Команда history. Показывает историю команд с поддержкой вывода последних n команд"""

    history_file = get_history_file()

    if not history_file.exists():
        return True, ["Истории команд пока нет"], False

    try:
        with open(history_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        if not lines:
            return True, ["Истории команд пока нет"], False

        if not args:
            output = []
            for i, line in enumerate(lines, 1):
                cleaned_cmd = line.strip()
                if cleaned_cmd:
                    output.append(f"{i:4d}  {cleaned_cmd}")
            return True, output, True

        if len(args) > 1:
            return False, ["ОШИБКА: история принимает не более одного аргумента"], False

        try:
            n = int(args[0])
            if n <= 0:
                return False, ["ОШИБКА: аргумент должен быть положительным"], False

            recent_commands = lines[-n:]
            output = []
            start_number = len(lines) - len(recent_commands) + 1

            for i, cmd in enumerate(recent_commands, start_number):
                cleaned_cmd = cmd.strip()
                if cleaned_cmd:
                    output.append(f"{i:4d}  {cleaned_cmd}")

            return True, output, True

        except ValueError:
            return False, ["ОШИБКА: аргумент должен быть целым числом"], False

    except Exception as e:
        return False, [f"ОШИБКА: {e}"], False