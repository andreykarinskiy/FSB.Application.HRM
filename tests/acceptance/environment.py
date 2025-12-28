from tests.acceptance.helpers.driver import CliDriver


def before_scenario(context, scenario):
    import sys
    context.sut = CliDriver(f"{sys.executable} -m hrm", 1.0)
    context.expected_candidates = list()
    
    context.sut.execute("clear", ["--force"])


def after_scenario(context, scenario):
    pass

