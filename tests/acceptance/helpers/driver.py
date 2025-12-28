import subprocess
import pexpect
from typing import Dict, Any

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
            cmd = [self.app_path, command] + (args or [])

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
                "return_code": result.returncode
            }

        except subprocess.TimeoutExpired as e:
            raise TimeoutError(f"Legacy application timed out after {self.app_timeout} seconds")

        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "stdout": e.stdout,
                "stderr": e.stderr,
                "return_code": e.returncode,
                "error": str(e)
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