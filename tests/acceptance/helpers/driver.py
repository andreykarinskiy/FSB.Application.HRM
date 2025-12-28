import subprocess
from typing import Optional, List, Any

try:
    import pexpect
except ImportError:
    pexpect = None  # pexpect не доступен на Windows


class CliResult:
    """
    Результат выполнения CLI команды.
    """
    
    def __init__(
        self,
        success: bool,
        stdout: str = "",
        stderr: str = "",
        return_code: int = 0,
        command: Optional[str] = None,
        error: Optional[str] = None
    ):
        self.success = success
        self.stdout = stdout
        self.stderr = stderr
        self.return_code = return_code
        self.command = command
        self.error = error
    
    def get_error_details(self) -> str:
        """
        Возвращает детали ошибки в виде строки.
        """
        error_details = []
        if self.command:
            error_details.append(f"Команда: {self.command}")
        if self.stdout:
            error_details.append(f"Stdout: {self.stdout}")
        if self.stderr:
            error_details.append(f"Stderr: {self.stderr}")
        return "\n".join(error_details) if error_details else "Детали ошибки отсутствуют"
    
    def get_error_message(self) -> str:
        """
        Возвращает полное сообщение об ошибке, включая детали.
        """
        error_msg = self.error or "Неизвестная ошибка"
        return f"{error_msg}\n{self.get_error_details()}"


class CliDriver:
    """
    Драйвер консольного приложения.
    """

    def __init__(self, app_path: str, app_timeout: float):
        self.app_path = app_path
        self.app_timeout = app_timeout


    def execute(self, command: str, args: list = None) -> CliResult:
        """
        Выполнение простой команды без интерактивного ввода
        """
        # Разбиваем app_path на части, если он содержит пробелы (например, "python -m hrm")
        app_path_parts = self.app_path.split()
        cmd = app_path_parts + [command] + (args or [])
        command_str = " ".join(cmd)
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.app_timeout,
                check=True
            )

            return CliResult(
                success=True,
                stdout=result.stdout,
                stderr=result.stderr,
                return_code=result.returncode,
                command=command_str
            )

        except subprocess.TimeoutExpired as e:
            raise TimeoutError(f"Команда '{command_str}' превысила время ожидания ({self.app_timeout} секунд)")

        except subprocess.CalledProcessError as e:
            error_message = f"Команда '{command_str}' завершилась с кодом {e.returncode}"
            if e.stderr:
                error_message += f"\nStderr: {e.stderr}"
            if e.stdout:
                error_message += f"\nStdout: {e.stdout}"
            
            return CliResult(
                success=False,
                stdout=e.stdout or "",
                stderr=e.stderr or "",
                return_code=e.returncode,
                error=error_message,
                command=command_str
            )

    def execute_interactive(self, command_sequence: list) -> CliResult:
        """
        Выполнение интерактивных команд с использованием pexpect
        """
        if pexpect is None:
            return CliResult(
                success=False,
                error="pexpect не доступен на этой платформе",
                command="interactive"
            )
        
        try:
            child = pexpect.spawn(self.app_path, timeout=self.app_timeout)

            output = []
            command_parts = []

            for step in command_sequence:
                if isinstance(step, str):  # Простая команда
                    child.sendline(step)
                    command_parts.append(step)
                elif isinstance(step, dict):  # С ожиданием ответа
                    child.expect(step["expect"])
                    child.sendline(step["send"])
                    command_parts.append(step.get("send", ""))
                    output.append(child.before.decode())

            child.expect(pexpect.EOF)
            output.append(child.before.decode())
            
            output_str = "\n".join(output)
            command_str = " ".join(command_parts) if command_parts else "interactive"

            return CliResult(
                success=True,
                stdout=output_str,
                stderr="",
                return_code=child.exitstatus if hasattr(child, 'exitstatus') else 0,
                command=command_str
            )

        except (pexpect.TIMEOUT, pexpect.EOF) as e:
            output_str = child.before.decode() if hasattr(child, 'before') else ""
            error_message = f"Интерактивная команда завершилась с ошибкой: {str(e)}"
            
            return CliResult(
                success=False,
                stdout=output_str,
                stderr="",
                return_code=1,
                error=error_message,
                command="interactive"
            )


class CliArgumentBuilder:
    """
    Построитель аргументов для CLI команд.
    Упрощает создание списка аргументов для команд.
    """

    def __init__(self):
        self._args: List[str] = []

    def add(self, flag: str, value: Optional[Any] = None) -> 'CliArgumentBuilder':
        """
        Добавляет аргумент в список.
        :param flag: Флаг команды (например, "--first-name")
        :param value: Значение аргумента. Если None, добавляется только флаг.
        :return: self для цепочки вызовов
        """
        self._args.append(flag)
        if value is not None:
            self._args.append(str(value))
        return self

    def add_if(self, flag: str, value: Optional[Any], condition: bool = True) -> 'CliArgumentBuilder':
        """
        Добавляет аргумент только если значение не None и condition == True.
        :param flag: Флаг команды (например, "--phone")
        :param value: Значение аргумента
        :param condition: Дополнительное условие для добавления
        :return: self для цепочки вызовов
        """
        if value is not None and condition:
            self.add(flag, value)
        return self

    def add_if_present(self, flag: str, value: Optional[Any]) -> 'CliArgumentBuilder':
        """
        Добавляет аргумент только если значение присутствует (не None и не пустая строка).
        :param flag: Флаг команды
        :param value: Значение аргумента
        :return: self для цепочки вызовов
        """
        if value is not None and value != "":
            self.add(flag, value)
        return self

    def build(self) -> List[str]:
        """
        Возвращает построенный список аргументов.
        :return: Список аргументов
        """
        return self._args.copy()

    def __iter__(self):
        """Позволяет использовать билдер напрямую в качестве итератора"""
        return iter(self._args)

    def __len__(self):
        """Возвращает количество аргументов"""
        return len(self._args)
