from pathlib import Path

from src.parser import parsing_and_checking_command
from src.errors import TerminalError
from src.commands.execution_command import command_execution
from src.logger import log_command


def main():
    print("Добро пожаловать в файловый терминал.\nВведите 'exit' для выхода или нажмите Ctrl + D\n")

    history_file = Path('.history')

    try:
        while True:
            try:
                current_directory = Path.cwd()
                input_text = input(f'{current_directory}$ ').strip()

                if input_text == 'exit':
                    print("До свидания!")
                    break
                elif not input_text:
                    continue

                with open(history_file, 'a', encoding='utf-8') as f:
                    f.write(input_text + '\n')

                command, args = parsing_and_checking_command(input_text)

                accuracy, result, cnt = command_execution(command, args)

                error_message = None
                if not accuracy and result:
                    error_message = result[0] if result else "Неизвестная ошибка"
                log_command(input_text, accuracy, error_message)

                if accuracy:
                    if cnt:
                        for line in result:
                            print(line)
                    else:
                        print(*result)
                else:
                    for error in result:
                        print(error)

            except EOFError:
                print("До свидания!")
                break
            except TerminalError as e:
                error_msg = str(e)
                print("ОШИБКА:", error_msg)
                log_command(input_text, False, error_msg)
            except Exception as e:
                error_msg = f"Непредвиденная ошибка: {e}"
                print(error_msg)
                log_command(input_text, False, error_msg)

    except KeyboardInterrupt:
        print("Введите 'exit' для выхода или нажмите Ctrl + D")


if __name__ == "__main__":
    main()