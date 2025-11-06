from colorama import init, Fore, Style

from src.parser import parsing_and_checking_command
from src.errors import TerminalError
from src.commands.execution_command import command_execution
from src.logger import log_command
from src.state import get_current_path, get_home_dir, get_history_file

init() # Инициализация colorama


def main():
    print("Добро пожаловать в файловый терминал.\nВведите 'exit' для выхода или нажмите Ctrl + D\n")

    try:
        while True:
            try:
                current_path = get_current_path()

                if current_path == get_home_dir():
                    path_display = "~"
                else:
                    path_display = current_path

                input_text = input(f'{Fore.GREEN}{path_display}${Style.RESET_ALL} ').strip()

                if input_text == 'exit':
                    print("До свидания!")
                    break
                elif not input_text:
                    continue

                with open(get_history_file(), 'a', encoding='utf-8') as f:
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
                        print(f"{Fore.RED}{error}{Style.RESET_ALL}")  # Красный цвет для ошибок

            except EOFError:
                print("До свидания!")
                break

            except TerminalError as e:
                error_msg = str(e)
                print(f"{Fore.RED}ОШИБКА: {error_msg}{Style.RESET_ALL}")
                log_command(input_text, False, error_msg)

            except Exception as e:
                error_msg = f"Непредвиденная ошибка: {e}"
                print(f"{Fore.RED}{error_msg}{Style.RESET_ALL}")
                log_command(input_text, False, error_msg)

    except KeyboardInterrupt:
        print("Введите 'exit' для выхода или нажмите Ctrl + D")


if __name__ == "__main__":
    main()