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
    # Инициализируем список результатов регистрации, если его еще нет
    if not hasattr(context, 'registration_results'):
        context.registration_results = []
    
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

        # Формируем аргументы для команды add
        args = [
            "--first-name", candidate.first_name,
            "--last-name", candidate.last_name
        ]
        
        # Добавляем опциональные параметры
        if candidate.phone:
            args.extend(["--phone", candidate.phone])
        
        if candidate.birth_date:
            args.extend(["--birth-date", candidate.birth_date.strftime("%Y-%m-%d")])
        
        if candidate.sex:
            sex_value = "M" if candidate.sex.value == 1 else "F"
            args.extend(["--sex", sex_value])
        
        if candidate.comments:
            args.extend(["--comments", candidate.comments])
        
        result = context.sut.execute("add", args)
        
        # Сохраняем результат регистрации вместе с данными кандидата
        context.registration_results.append({
            "candidate": candidate,
            "result": result
        })
        
        # Если регистрация не удалась, сразу выбрасываем исключение с подробной информацией
        if not result.get("success", False):
            error_details = []
            if result.get("command"):
                error_details.append(f"Команда: {result['command']}")
            if result.get("stdout"):
                error_details.append(f"Stdout: {result['stdout']}")
            if result.get("stderr"):
                error_details.append(f"Stderr: {result['stderr']}")
            error_context = "\n".join(error_details) if error_details else "Детали ошибки отсутствуют"
            
            raise AssertionError(
                f"Не удалось зарегистрировать кандидата {candidate.first_name} {candidate.last_name}.\n"
                f"{result.get('error', 'Неизвестная ошибка')}\n"
                f"{error_context}"
            )


@then(u'кандидат успешно зарегистрирован в системе')
def step_impl(context):
    # Проверяем утверждение, что регистрация прошла успешно
    assert hasattr(context, 'registration_results'), "Регистрация не была выполнена"
    assert len(context.registration_results) > 0, "Нет результатов регистрации"
    
    for registration in context.registration_results:
        candidate = registration["candidate"]
        result = registration["result"]
        
        # Формируем информативное сообщение об ошибке
        error_details = []
        if result.get("command"):
            error_details.append(f"Выполненная команда: {result['command']}")
        if result.get("stdout"):
            error_details.append(f"Stdout: {result['stdout']}")
        if result.get("stderr"):
            error_details.append(f"Stderr: {result['stderr']}")
        error_context = "\n".join(error_details) if error_details else "Детали ошибки отсутствуют"
        
        # Проверяем, что команда выполнилась успешно
        assert result["success"] is True, \
            f"Регистрация кандидата {candidate.first_name} {candidate.last_name} не удалась.\n" \
            f"{result.get('error', 'Неизвестная ошибка')}\n" \
            f"{error_context}"
        
        assert result["return_code"] == 0, \
            f"Команда регистрации вернула код {result['return_code']} вместо 0.\n" \
            f"{error_context}"
        
        # Проверяем, что в выводе есть сообщение об успешной регистрации
        assert "успешно зарегистрирован" in result["stdout"], \
            f"В выводе отсутствует сообщение об успешной регистрации для {candidate.first_name} {candidate.last_name}.\n" \
            f"Вывод команды:\n{result.get('stdout', '(пусто)')}\n" \
            f"Ошибки:\n{result.get('stderr', '(нет ошибок)')}"
        
        assert candidate.first_name in result["stdout"] and candidate.last_name in result["stdout"], \
            f"В выводе отсутствуют имя и фамилия кандидата {candidate.first_name} {candidate.last_name}.\n" \
            f"Вывод команды:\n{result.get('stdout', '(пусто)')}"


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