from abc import ABC

from tests.acceptance.helpers.driver import CliDriver


class SystemFacade(ABC):
    """
    Контракт для тестируемой системы.
    Упрощает написание тестовой логики, пряча за простым интерфейсом детали реализации системы.
    """
    pass


class CliSystemFacade(SystemFacade):
    """
    Реализация фасада для консольного приложения.
    """
    
    def __init__(self, driver: CliDriver):
        self.driver = driver
    
    def execute(self, command: str, args: list = None):
        """
        Выполняет команду через драйвер.
        :param command: Команда для выполнения
        :param args: Аргументы команды
        :return: Результат выполнения команды
        """
        return self.driver.execute(command, args)
    