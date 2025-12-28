import subprocess
from typing import Dict, Any

try:
    import pexpect
except ImportError:
    pexpect = None  # pexpect не доступен на Windows

class CliDriver:
    """
    Драйвер консольного приложения.
    """

    def __init__(self, app_path: str, app_timeout: float):
        self.app_path = app_path
        self.app_timeout = app_timeout


    def execute(self, command: str, args: list = None) -> Dict[str, Any]:
        """
        Выполнение простой команды без интерактивного ввода
        """
        try:
            # Разбиваем app_path на части, если он содержит пробелы (например, "python -m hrm")
            app_path_parts = self.app_path.split()
            cmd = app_path_parts + [command] + (args or [])

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.app_timeout,
                check=True
            )

            return {
                "success": True,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
                "command": " ".join(cmd)
            }

        except subprocess.TimeoutExpired as e:
            raise TimeoutError(f"Команда '{' '.join(cmd)}' превысила время ожидания ({self.app_timeout} секунд)")

        except subprocess.CalledProcessError as e:
            error_message = f"Команда '{' '.join(cmd)}' завершилась с кодом {e.returncode}"
            if e.stderr:
                error_message += f"\nStderr: {e.stderr}"
            if e.stdout:
                error_message += f"\nStdout: {e.stdout}"
            
            return {
                "success": False,
                "stdout": e.stdout or "",
                "stderr": e.stderr or "",
                "return_code": e.returncode,
                "error": error_message,
                "command": " ".join(cmd)
            }

    def execute_interactive(self, command_sequence: list) -> Dict[str, Any]:
        """
        Выполнение интерактивных команд с использованием pexpect
        """
        try:
            child = pexpect.spawn(self.app_path, timeout=self.app_timeout)

            output = []

            for step in command_sequence:
                if isinstance(step, str):  # Простая команда
                    child.sendline(step)
                elif isinstance(step, dict):  # С ожиданием ответа
                    child.expect(step["expect"])
                    child.sendline(step["send"])
                    output.append(child.before.decode())

            child.expect(pexpect.EOF)
            output.append(child.before.decode())

            return {
                "success": True,
                "output": "\n".join(output),
                "exit_status": child.exitstatus
            }

        except (pexpect.TIMEOUT, pexpect.EOF) as e:
            return {
                "success": False,
                "error": str(e),
                "output": child.before.decode() if hasattr(child, 'before') else ""
            }