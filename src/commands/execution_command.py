from src.commands.command_ls import command_ls
from src.commands.command_cd import command_cd
from src.commands.command_cat import command_cat
from src.commands.command_cp import command_cp
from src.commands.command_mv import command_mv
from src.commands.command_rm import command_rm
from src.commands.command_zip import command_zip
from src.commands.command_unzip import command_unzip
from src.commands.command_tar import command_tar
from src.commands.command_untar import command_untar
from src.commands.command_grep import command_grep
from src.commands.command_history import command_history
from src.commands.command_undo import command_undo

def command_execution(command: str, args: list):
    """Передает выполнение функциям, в зависимости от команды."""

    try:
        match command:
            case 'ls':
                return command_ls(args)
            case 'cd':
                return command_cd(args)
            case 'cat':
                return command_cat(args)
            case 'cp':
                return command_cp(args)
            case 'mv':
                return command_mv(args)
            case 'rm':
                return command_rm(args)
            case 'zip':
                return command_zip(args)
            case 'unzip':
                return command_unzip(args)
            case 'tar':
                return command_tar(args)
            case 'untar':
                return command_untar(args)
            case 'grep':
                return command_grep(args)
            case 'history':
                return command_history(args)
            case 'undo':
                return command_undo(args)
            case _:
                return False, [f"Command {command} not found"], False

    except Exception as e:
        return False, [f"ERROR: {e}"], False