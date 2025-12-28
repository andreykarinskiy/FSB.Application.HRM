from datetime import datetime
from behave import given, when, then
from hrm.core.model import Candidate, CandidateStatus, CandidateSex
from tests.acceptance.helpers.driver import CliArgumentBuilder


def parse_sex(text):
    if text == "M":
        return CandidateSex.MALE
    elif text == "F":
        return CandidateSex.FEMALE
    elif text == "":
        return None
    raise ValueError(f"Invalid sex: {text}")


def parse_date(text):
    return datetime.strptime(text, "%Y-%m-%d") if text != "" else None


@given(u'система готова к регистрации кандидатов')
def step_impl(context):
    pass


@when(u'я регистрирую кандидата со следующими данными:')
def step_impl(context):
    for row in context.table:
        candidate = Candidate(
            id=None,
            first_name=row["Имя"],
            last_name=row["Фамилия"],
            phone=row["Телефон"],
            sex=parse_sex(row["Пол"]),
            birth_date=parse_date(row["Дата рождения"]),
            comments=row["Комментарии"],
            status=CandidateStatus.REGISTERED
        )

        # TODO: Поискать, нет ли в Behave удобного механизма конвертеров значений.
        sex_value = None
        if candidate.sex:
            sex_value = "M" if candidate.sex.value == 1 else "F"
        birth_date_str = candidate.birth_date.strftime("%Y-%m-%d") if candidate.birth_date else None
        
        args = CliArgumentBuilder() \
            .add("--first-name", candidate.first_name) \
            .add("--last-name", candidate.last_name) \
            .add_if_present("--phone", candidate.phone) \
            .add_if_present("--birth-date", birth_date_str) \
            .add_if_present("--sex", sex_value) \
            .add_if_present("--comments", candidate.comments) \
            .build()
        
        result = context.sut.execute("add", args)

        expected_and_result = (candidate, result)
        context.expected_candidates.append(expected_and_result)
        
        # if not result.success:
        #     raise AssertionError(
        #         f"Не удалось зарегистрировать кандидата {candidate.first_name} {candidate.last_name}.\n"
        #         f"{result.get_error_message()}"
        #     )


@then(u'кандидат успешно зарегистрирован в системе')
def step_impl(context):



    # Проверяем утверждение, что регистрация прошла успешно
    # assert hasattr(context, 'registration_results'), "Регистрация не была выполнена"
    # assert len(context.registration_results) > 0, "Нет результатов регистрации"
    #
    # for registration in context.registration_results:
    #     candidate = registration["candidate"]
    #     result = registration["result"]
    #
    #     # Проверяем, что команда выполнилась успешно
    #     assert result.success is True, \
    #         f"Регистрация кандидата {candidate.first_name} {candidate.last_name} не удалась.\n" \
    #         f"{result.get_error_message()}"
    #
    #     assert result.return_code == 0, \
    #         f"Команда регистрации вернула код {result.return_code} вместо 0.\n" \
    #         f"{result.get_error_details()}"
    #
    #     # Проверяем, что в выводе есть сообщение об успешной регистрации
    #     assert "успешно зарегистрирован" in result.stdout, \
    #         f"В выводе отсутствует сообщение об успешной регистрации для {candidate.first_name} {candidate.last_name}.\n" \
    #         f"Вывод команды:\n{result.stdout or '(пусто)'}\n" \
    #         f"Ошибки:\n{result.stderr or '(нет ошибок)'}"
    #
    #     assert candidate.first_name in result.stdout and candidate.last_name in result.stdout, \
    #         f"В выводе отсутствуют имя и фамилия кандидата {candidate.first_name} {candidate.last_name}.\n" \
    #         f"Вывод команды:\n{result.stdout or '(пусто)'}"
    pass


@then(u'кандидату присвоен уникальный идентификатор')
def step_impl(context):
    pass


@then(u'статус кандидата установлен в "REGISTERED"')
def step_impl(context):
    pass


@then(u'кандидат может быть получен из системы по его идентификатору')
def step_impl(context):
    pass


@then(u'данные кандидата соответствуют введенным данным')
def step_impl(context):
    pass