from pathlib import Path


def command_history(args: str) -> (bool, list, bool):
    """Показывает историю команд с поддержкой вывода последних n команд"""

    history_file = Path('.history')

    if not history_file.exists():
        return True, ["Истории команд пока нет"], False

    try:
        with open(history_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        if not lines:
            return True, ["Истории команд пока нет"], False

        n = 10
        if args:
            if len(args) > 1:
                return False, ["ОШИБКА: история принимает не более одного аргумента"], False

            try:
                n = int(args[0])
                if n <= 0:
                    return False, ["ОШИБКА: аргумент должен быть положительным"], False

                if n > len(lines):
                    n = len(lines)
            except ValueError:
                return False, ["ОШИБКА: аргумент должен быть целым числом"], False

        recent_commands = lines[:-1]

        if len(recent_commands) < n:
            recent_commands = lines[:]
            if recent_commands and recent_commands[-1].strip().startswith('history'):
                recent_commands = recent_commands[:-1]

        recent_commands = recent_commands[-n:] if len(recent_commands) > n else recent_commands

        output = []

        for cmd in recent_commands:
            cleaned_cmd = cmd.strip()
            if cleaned_cmd:
                output.append(cleaned_cmd)

        return True, output, True

    except Exception as e:
        return False, [f"ОШИБКА: {e}"], False