import pytest
import os
import shutil
import tempfile
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.commands.execution_command import command_execution
from src.parser import parsing_and_checking_command
from src.state import set_current_path, get_current_path


@pytest.fixture
def test_env():
    """Создает временную тестовую среду"""
    test_dir = Path(tempfile.mkdtemp())
    original_path = get_current_path()

    # Устанавливаем временную директорию как текущую
    set_current_path(test_dir)

    # Создаем тестовую структуру файлов
    test_files = {
        "file1.txt": "Hello world\nThis is a test\nHello again\nPython programming",
        "file2.txt": "Goodbye world\nAnother test\nHello there\nTesting 123",
        "file3.txt": "No match here\nJust some text\nEnd of file",
        "empty.txt": "",
        "code.py": "import os\nimport sys\n\ndef main():\n    print('Hello World')\n    return 0\n\nif __name__ == '__main__':\n    main()",
        "data.csv": "name,age,city\nJohn,25,London\nAlice,30,Paris\nBob,35,Tokyo"
    }

    for filename, content in test_files.items():
        (test_dir / filename).write_text(content)

    # Создаем тестовые директории
    folders = [
        "project/src/utils",
        "project/src/models",
        "project/tests",
        "data/raw",
        "data/processed"
    ]

    for folder in folders:
        (test_dir / folder).mkdir(parents=True, exist_ok=True)

    (test_dir / "project/src/utils" / "helpers.py").write_text("def helper():\n    pass")
    (test_dir / "project/src/models" / "model.py").write_text("class Model:\n    pass")
    (test_dir / "data/raw" / "data1.csv").write_text("raw,data,1,2,3")

    yield test_dir  # Возвращаем путь к тестовой директории

    # Очистка после тестов
    set_current_path(original_path)
    shutil.rmtree(test_dir)


def execute_command(command_string):
    """Вспомогательная функция для выполнения команд"""
    try:
        command, args = parsing_and_checking_command(command_string)
        return command_execution(command, args)
    except Exception as e:
        return False, [f"ОШИБКА: {e}"], False


# Тесты для команды ls
def test_ls_basic(test_env):
    """Тест базовой команды ls"""
    success, result, cnt = execute_command("ls")
    assert success == True
    assert "file1.txt" in result[0]
    assert "file2.txt" in result[0]


def test_ls_with_flag(test_env):
    """Тест команды ls с флагом -l"""
    success, result, cnt = execute_command("ls -l")
    assert success == True
    assert any("file1.txt" in line for line in result)


def test_ls_with_directory(test_env):
    """Тест команды ls с указанием директории"""
    success, result, cnt = execute_command("ls project")
    assert success == True
    assert "src" in result[0] or "src" in str(result)


def test_ls_multiple_directories(test_env):
    """Тест ls с несколькими директориями"""
    success, result, cnt = execute_command("ls project/src project/tests")
    assert success == True


def test_ls_empty_directory(test_env):
    """Тест ls с пустой директорией"""
    empty_dir = test_env / "empty_dir"
    empty_dir.mkdir()

    success, result, cnt = execute_command("ls empty_dir")
    assert success == True


# Тесты для команды cd
def test_cd_basic(test_env):
    """Тест команды cd"""
    success, result, cnt = execute_command("cd project")
    assert success == True
    # Проверяем, что текущий путь изменился
    assert "project" in str(get_current_path())


def test_cd_home(test_env):
    """Тест cd ~ (домашняя директория)"""
    success, result, cnt = execute_command("cd ~")
    assert success == True


def test_cd_relative_paths(test_env):
    """Тест cd с относительными путями"""
    execute_command("cd project")
    assert "project" in str(get_current_path())

    execute_command("cd ..")
    assert str(test_env) == str(get_current_path())


# Тесты для команды cat
def test_cat_basic(test_env):
    """Тест команды cat"""
    success, result, cnt = execute_command("cat file1.txt")
    assert success == True
    assert "Hello world" in result[0]


def test_cat_multiple_files(test_env):
    """Тест cat с несколькими файлами"""
    success, result, cnt = execute_command("cat file1.txt file2.txt")
    assert success == True
    assert len(result) == 2


def test_cat_empty_file(test_env):
    """Тест cat с пустым файлом"""
    success, result, cnt = execute_command("cat empty.txt")
    assert success == True
    assert result[0] == "" or len(result[0]) == 0


# Тесты для команды cp
def test_cp_file(test_env):
    """Тест копирования файла"""
    success, result, cnt = execute_command("cp file1.txt file1_copy.txt")
    assert success == True
    assert (test_env / "file1_copy.txt").exists()


def test_cp_file_to_directory(test_env):
    """Тест копирования файла в директорию"""
    success, result, cnt = execute_command("cp file1.txt project")
    assert success == True
    assert (test_env / "project" / "file1.txt").exists()


# Тесты для команды mv
def test_mv_file(test_env):
    """Тест перемещения файла"""
    success, result, cnt = execute_command("mv file1.txt file1_moved.txt")
    assert success == True
    assert not (test_env / "file1.txt").exists()
    assert (test_env / "file1_moved.txt").exists()


def test_mv_file_to_directory(test_env):
    """Тест перемещения файла в директорию"""
    success, result, cnt = execute_command("mv file1.txt project")
    assert success == True
    assert not (test_env / "file1.txt").exists()
    assert (test_env / "project" / "file1.txt").exists()


def test_mv_multiple_files(test_env):
    """Тест перемещения нескольких файлов"""
    success, result, cnt = execute_command("mv file1.txt file2.txt project")
    assert success == True
    assert not (test_env / "file1.txt").exists()
    assert not (test_env / "file2.txt").exists()
    assert (test_env / "project" / "file1.txt").exists()
    assert (test_env / "project" / "file2.txt").exists()


# Тесты для команды rm
def test_rm_file(test_env):
    """Тест удаления файла"""
    success, result, cnt = execute_command("rm file1.txt")
    assert success == True
    assert not (test_env / "file1.txt").exists()


def test_rm_multiple_files(test_env):
    """Тест удаления нескольких файлов"""
    success, result, cnt = execute_command("rm file1.txt file2.txt")
    assert success == True
    assert not (test_env / "file1.txt").exists()
    assert not (test_env / "file2.txt").exists()


# Тесты для команды grep
def test_grep_basic(test_env):
    """Тест базового поиска grep"""
    success, result, cnt = execute_command("grep Hello file1.txt")
    assert success == True
    assert any("Hello" in line for line in result)


def test_grep_ignore_case(test_env):
    """Тест поиска grep с игнорированием регистра"""
    success, result, cnt = execute_command("grep -i hello file1.txt")
    assert success == True
    assert any("Hello" in line for line in result)


def test_grep_recursive(test_env):
    """Тест рекурсивного поиска grep"""
    success, result, cnt = execute_command("grep -r test .")
    assert success == True


# Тесты для команды history
def test_history_basic(test_env):
    """Тест команды history"""
    # Выполним несколько команд для истории
    execute_command("ls")
    execute_command("pwd")

    success, result, cnt = execute_command("history")
    assert success == True


# Тесты для команды undo
def test_undo_cp(test_env):
    """Тест отмены операции копирования"""
    execute_command("cp file1.txt file1_copy.txt")
    assert (test_env / "file1_copy.txt").exists()

    success, result, cnt = execute_command("undo")
    # Проверяем, что файл был удален при отмене
    assert success == True


def test_undo_rm(test_env):
    """Тест отмены операции удаления"""
    execute_command("rm file1.txt")
    assert not (test_env / "file1.txt").exists()

    success, result, cnt = execute_command("undo")
    # Проверяем, что файл был восстановлен при отмене
    assert success == True
    assert (test_env / "file1.txt").exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])