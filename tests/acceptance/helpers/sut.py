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
    