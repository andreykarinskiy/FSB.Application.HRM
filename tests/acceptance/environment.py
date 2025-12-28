from tests.acceptance.helpers.driver import CliDriver
from tests.acceptance.helpers.sut import CliSystemFacade


def before_scenario(context, scenario):
    # context.sut = CliSystemFacade(CliDriver("hrm", 1.0))
    import sys
    context.sut = CliDriver(f"{sys.executable} -m hrm", 1.0)
    context.expected_candidates = list()
    
    # Очищаем репозиторий перед каждым сценарием
    clear_result = context.sut.execute("clear", ["--force"])
    if not clear_result.get("success", False):
        error_details = []
        if clear_result.get("command"):
            error_details.append(f"Команда: {clear_result['command']}")
        if clear_result.get("stdout"):
            error_details.append(f"Stdout: {clear_result['stdout']}")
        if clear_result.get("stderr"):
            error_details.append(f"Stderr: {clear_result['stderr']}")
        error_context = "\n".join(error_details) if error_details else "Детали ошибки отсутствуют"
        
        raise AssertionError(
            f"Не удалось очистить репозиторий перед сценарием.\n"
            f"{clear_result.get('error', 'Неизвестная ошибка')}\n"
            f"{error_context}"
        )


def after_scenario(context, scenario):
    pass

