from tests.acceptance.helpers.driver import CliDriver
from tests.acceptance.helpers.sut import CliSystemFacade


def before_scenario(context, scenario):
    context.sut = CliSystemFacade(CliDriver("hrm", 1.0))
    context.expected_candidates = list()


def after_scenario(context, scenario):
    pass

