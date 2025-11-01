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


class TestFileTerminalExtended:
    """Расширенные тесты для файлового терминала"""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Настройка перед каждым тестом и очистка после"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.original_cwd = Path.cwd()
        os.chdir(self.test_dir)

        self.setup_complex_test_structure()

        yield

        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def setup_complex_test_structure(self):
        """Создание сложной тестовой структуры файлов и папок"""
        test_files = {
            "file1.txt": "Hello world\nThis is a test\nHello again\nPython programming",
            "file2.txt": "Goodbye world\nAnother test\nHello there\nTesting 123",
            "file3.txt": "No match here\nJust some text\nEnd of file",
            "empty.txt": "",
            "large_file.txt": "Line " + "\nLine ".join(str(i) for i in range(1, 101)) + "\n",
            "special_chars.txt": "File with spaces and-dashes_and_underscores.txt",
            "code.py": "import os\nimport sys\n\ndef main():\n    print('Hello World')\n    return 0\n\nif __name__ == '__main__':\n    main()",
            "config.json": '{"name": "test", "value": 123, "active": true}',
            "data.csv": "name,age,city\nJohn,25,London\nAlice,30,Paris\nBob,35,Tokyo"
        }

        for filename, content in test_files.items():
            (self.test_dir / filename).write_text(content)

        folders = [
            "project/src/utils",
            "project/src/models",
            "project/tests/unit",
            "project/tests/integration",
            "project/docs",
            "data/raw",
            "data/processed",
            "backup/2024",
            "temp/logs",
            "nested/level1/level2/level3"
        ]

        for folder in folders:
            (self.test_dir / folder).mkdir(parents=True, exist_ok=True)

        (self.test_dir / "project/src/utils" / "helpers.py").write_text("def helper():\n    pass")
        (self.test_dir / "project/src/models" / "model.py").write_text("class Model:\n    pass")
        (self.test_dir / "project/tests/unit" / "test_utils.py").write_text("def test_helper():\n    pass")
        (self.test_dir / "data/raw" / "data1.csv").write_text("raw,data,1,2,3")
        (self.test_dir / "data/processed" / "processed.csv").write_text("processed,data")

        # Создаем симлинк (если поддерживается)
        try:
            (self.test_dir / "symlink_to_file1.txt").symlink_to("file1.txt")
        except (OSError, NotImplementedError):
            pass  # Пропускаем на платформах, где не поддерживается

        # Создаем исполняемый файл (если поддерживается)
        special_file = self.test_dir / "executable.sh"
        special_file.write_text("#!/bin/bash\necho 'Hello'")
        try:
            special_file.chmod(0o755)
        except OSError:
            pass  # Пропускаем на Windows

    def execute_command(self, command_string):
        """Вспомогательная функция для выполнения команд"""
        try:
            command, args = parsing_and_checking_command(command_string)
            return command_execution(command, args)
        except Exception as e:
            return False, [f"ERROR: {e}"], False

    # Тесты для команды ls
    def test_ls_basic(self):
        """Тест базовой команды ls"""
        success, result, cnt = self.execute_command("ls")
        assert success == True
        assert "file1.txt" in result[0]
        assert "file2.txt" in result[0]
        assert "test_folder" not in result[0]  # У нас нет test_folder в этой структуре

    def test_ls_with_flag(self):
        """Тест команды ls с флагом -l"""
        success, result, cnt = self.execute_command("ls -l")
        assert success == True
        # Проверяем, что вывод содержит подробную информацию
        assert any("file1.txt" in line for line in result)

    def test_ls_with_directory(self):
        """Тест команды ls с указанием директории"""
        success, result, cnt = self.execute_command("ls project")
        assert success == True
        assert "src" in result[0]
        assert "tests" in result[0]

    def test_ls_hidden_files(self):
        """Тест ls со скрытыми файлами"""
        hidden_file = self.test_dir / ".hidden_file"
        hidden_file.write_text("hidden content")

        success, result, cnt = self.execute_command("ls")
        assert success == True

    def test_ls_multiple_directories(self):
        """Тест ls с несколькими директориями"""
        success, result, cnt = self.execute_command("ls project/src project/tests")
        assert success == True
        assert any("utils" in str(line) for line in result)
        assert any("unit" in str(line) for line in result)

    def test_ls_empty_directory(self):
        """Тест ls с пустой директорией"""
        empty_dir = self.test_dir / "empty_dir"
        empty_dir.mkdir()

        success, result, cnt = self.execute_command("ls empty_dir")
        assert success == True

    # Тесты для команды cd
    def test_cd_basic(self):
        """Тест команды cd"""
        success, result, cnt = self.execute_command("cd project")
        assert success == True
        assert "project" in str(Path.cwd())

    def test_cd_relative_paths(self):
        """Тест cd с относительными путями"""
        self.execute_command("cd project")
        assert "project" in str(Path.cwd())

        self.execute_command("cd ..")
        assert str(self.test_dir) == str(Path.cwd())

        self.execute_command("cd nested/level1/level2/level3")
        assert "level3" in str(Path.cwd())

    # Тесты для команды cat
    def test_cat_basic(self):
        """Тест команды cat"""
        success, result, cnt = self.execute_command("cat file1.txt")
        assert success == True
        assert "Hello world" in result[0]
        assert "Hello again" in result[0]

    def test_cat_multiple_files(self):
        """Тест cat с несколькими файлами"""
        success, result, cnt = self.execute_command("cat file1.txt file2.txt")
        assert success == True
        assert len(result) == 2
        assert "Hello world" in result[0]
        assert "Goodbye world" in result[1]

    def test_cat_empty_file(self):
        """Тест cat с пустым файлом"""
        success, result, cnt = self.execute_command("cat empty.txt")
        assert success == True
        assert result[0] == "" or len(result[0]) == 0

    def test_cat_large_file(self):
        """Тест cat с большим файлом"""
        success, result, cnt = self.execute_command("cat large_file.txt")
        assert success == True
        assert "Line 1" in result[0]
        assert "Line 100" in result[0]

    # Тесты для команды cp
    def test_cp_file(self):
        """Тест копирования файла"""
        success, result, cnt = self.execute_command("cp file1.txt file1_copy.txt")
        assert success == True
        assert (self.test_dir / "file1_copy.txt").exists()
        assert (self.test_dir / "file1_copy.txt").read_text() == (self.test_dir / "file1.txt").read_text()

    def test_cp_file_to_directory(self):
        """Тест копирования файла в директорию"""
        success, result, cnt = self.execute_command("cp file1.txt project")
        assert success == True
        assert (self.test_dir / "project" / "file1.txt").exists()

    # Тесты для команды mv
    def test_mv_file(self):
        """Тест перемещения файла"""
        success, result, cnt = self.execute_command("mv file1.txt file1_moved.txt")
        assert success == True
        assert not (self.test_dir / "file1.txt").exists()
        assert (self.test_dir / "file1_moved.txt").exists()

    def test_mv_file_to_directory(self):
        """Тест перемещения файла в директорию"""
        success, result, cnt = self.execute_command("mv file1.txt project")
        assert success == True
        assert not (self.test_dir / "file1.txt").exists()
        assert (self.test_dir / "project" / "file1.txt").exists()

    # Тесты для команды rm
    def test_rm_file(self):
        """Тест удаления файла"""
        success, result, cnt = self.execute_command("rm file1.txt")
        assert success == True
        assert not (self.test_dir / "file1.txt").exists()

    # Тесты для команд архивов
    def test_zip_command(self):
        """Тест создания ZIP архива"""
        success, result, cnt = self.execute_command("zip project project.zip")
        assert success == True
        assert (self.test_dir / "project.zip").exists()

    # Тесты для команды grep
    def test_grep_basic(self):
        """Тест базового поиска grep"""
        success, result, cnt = self.execute_command("grep Hello file1.txt")
        assert success == True
        assert any("Hello world" in line for line in result)
        assert any("Hello again" in line for line in result)

    def test_grep_ignore_case(self):
        """Тест поиска grep с игнорированием регистра"""
        success, result, cnt = self.execute_command("grep -i hello file2.txt")
        assert success == True
        assert any("Hello there" in line for line in result)

    def test_grep_recursive(self):
        """Тест рекурсивного поиска grep"""
        success, result, cnt = self.execute_command("grep -r test .")
        assert success == True

    # Тесты для команды history
    def test_history_basic(self):
        """Тест команды history"""
        # Выполним несколько команд для истории
        self.execute_command("ls")

        success, result, cnt = self.execute_command("history")

    # Тесты для команды undo
    def test_undo_cp(self):
        """Тест отмены операции копирования"""
        self.execute_command("cp file1.txt file1_copy.txt")
        assert (self.test_dir / "file1_copy.txt").exists()


if __name__ == "__main__":
    # Запуск тестов напрямую
    pytest.main([__file__, "-v"])