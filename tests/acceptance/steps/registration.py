from datetime import datetime
from behave import given, when, then
from hrm.core.model import Candidate, CandidateStatus, CandidateSex


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
        context.expected_candidates.append(candidate)


@then(u'кандидат успешно зарегистрирован в системе')
def step_impl(context):
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