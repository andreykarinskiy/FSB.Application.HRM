from tests.acceptance.helpers.driver import CliDriver


def before_scenario(context, scenario):
    # context.sut = CliSystemFacade(CliDriver("hrm", 1.0))
    import sys
    context.sut = CliDriver(f"{sys.executable} -m hrm", 1.0)
    context.expected_candidates = list()
    
    # Очищаем репозиторий перед каждым сценарием
    context.sut.execute("clear", ["--force"])


def after_scenario(context, scenario):
    pass

