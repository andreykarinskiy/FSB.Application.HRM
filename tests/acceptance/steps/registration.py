import re
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


def extract_field_from_output(output: str, field_name: str) -> str:
    """
    Извлекает значение поля из вывода команды get.
    :param output: Вывод команды
    :param field_name: Название поля (например, "Имя", "Фамилия")
    :return: Значение поля или None, если не найдено
    """
    pattern = rf'{field_name}:\s*(.+)'
    match = re.search(pattern, output)
    return match.group(1).strip() if match else None


def extract_sex_from_output(output: str) -> str:
    """
    Извлекает пол из вывода команды get.
    :param output: Вывод команды
    :return: "M" для Мужской, "F" для Женский, None если не указан
    """
    pattern = r'Пол:\s*(Мужской|Женский)'
    match = re.search(pattern, output)
    if match:
        sex_text = match.group(1)
        return "M" if sex_text == "Мужской" else "F"
    return None


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


@then(u'кандидат успешно зарегистрирован в системе')
def step_impl(context):
    for expected_and_result in context.expected_candidates:
        candidate = expected_and_result[0]
        result = expected_and_result[1]

        assert result.success is True, \
            f"Не удалось зарегистрировать кандидата {candidate.first_name} {candidate.last_name}.\n" \
            f"{result.get_error_message()}"

        assert result.return_code == 0, \
            f"Команда регистрации вернула код {result.return_code} вместо 0.\n" \
            f"{result.get_error_details()}"


@then(u'кандидату присвоен уникальный идентификатор')
def step_impl(context):
    # Инициализируем список ID, если его еще нет
    if not hasattr(context, 'candidate_ids'):
        context.candidate_ids = []

    # Извлекаем ID из вывода для каждого кандидата
    for expected_and_result in context.expected_candidates:
        candidate = expected_and_result[0]
        result = expected_and_result[1]

        # Ищем ID в выводе команды (формат: "с ID: {id}")
        # Используем регулярное выражение для поиска ID
        id_pattern = r'с ID:\s*(\d+)'
        match = re.search(id_pattern, result.stdout)

        assert match is not None, \
            f"Не удалось найти ID в выводе для кандидата {candidate.first_name} {candidate.last_name}.\n" \
            f"Вывод команды:\n{result.stdout}"

        candidate_id = int(match.group(1))

        # Проверяем, что ID является положительным числом
        assert candidate_id > 0, \
            f"ID кандидата должен быть положительным числом, получен: {candidate_id}"

        # Сохраняем ID для проверки уникальности
        context.candidate_ids.append(candidate_id)

    # Проверяем уникальность всех ID
    unique_ids = set(context.candidate_ids)
    assert len(unique_ids) == len(context.candidate_ids), \
        f"Найдены дублирующиеся ID: {context.candidate_ids}. " \
        f"Уникальные ID: {unique_ids}"


@then(u'статус кандидата установлен в "REGISTERED"')
def step_impl(context):
    # Проверяем статус для каждого кандидата
    for expected_and_result in context.expected_candidates:
        candidate = expected_and_result[0]
        registration_result = expected_and_result[1]
        
        # Извлекаем ID из результата регистрации
        id_pattern = r'с ID:\s*(\d+)'
        match = re.search(id_pattern, registration_result.stdout)
        
        assert match is not None, \
            f"Не удалось найти ID для проверки статуса кандидата {candidate.first_name} {candidate.last_name}"
        
        candidate_id = int(match.group(1))
        
        # Получаем информацию о кандидате через команду get
        args = CliArgumentBuilder() \
            .add("--id", candidate_id) \
            .build()
        
        get_result = context.sut.execute("get", args)
        
        # Проверяем, что команда выполнилась успешно
        assert get_result.success is True, \
            f"Не удалось получить информацию о кандидате {candidate.first_name} {candidate.last_name} с ID {candidate_id}.\n" \
            f"{get_result.get_error_message()}"
        
        # Проверяем, что статус равен REGISTERED
        status_pattern = r'Статус:\s*(\w+)'
        status_match = re.search(status_pattern, get_result.stdout)
        
        assert status_match is not None, \
            f"Не удалось найти статус в выводе для кандидата {candidate.first_name} {candidate.last_name}.\n" \
            f"Вывод команды:\n{get_result.stdout}"
        
        actual_status = status_match.group(1)
        assert actual_status == "REGISTERED", \
            f"Статус кандидата {candidate.first_name} {candidate.last_name} (ID: {candidate_id}) равен '{actual_status}', " \
            f"ожидался 'REGISTERED'.\nВывод команды:\n{get_result.stdout}"


@then(u'кандидат может быть получен из системы по его идентификатору')
def step_impl(context):
    # Проверяем, что каждый кандидат может быть получен по его ID
    for expected_and_result in context.expected_candidates:
        candidate = expected_and_result[0]
        registration_result = expected_and_result[1]
        
        # Извлекаем ID из результата регистрации
        id_pattern = r'с ID:\s*(\d+)'
        match = re.search(id_pattern, registration_result.stdout)
        
        assert match is not None, \
            f"Не удалось найти ID для получения кандидата {candidate.first_name} {candidate.last_name}"
        
        candidate_id = int(match.group(1))
        
        # Получаем информацию о кандидате через команду get
        args = CliArgumentBuilder() \
            .add("--id", candidate_id) \
            .build()
        
        get_result = context.sut.execute("get", args)
        
        # Проверяем, что команда выполнилась успешно
        assert get_result.success is True, \
            f"Не удалось получить кандидата {candidate.first_name} {candidate.last_name} по ID {candidate_id}.\n" \
            f"{get_result.get_error_message()}"
        
        assert get_result.return_code == 0, \
            f"Команда get вернула код {get_result.return_code} вместо 0 для кандидата с ID {candidate_id}.\n" \
            f"{get_result.get_error_details()}"
        
        # Проверяем, что в выводе есть информация о кандидате
        assert candidate.first_name in get_result.stdout, \
            f"В выводе команды get отсутствует имя кандидата {candidate.first_name} {candidate.last_name}.\n" \
            f"Вывод команды:\n{get_result.stdout}"
        
        assert candidate.last_name in get_result.stdout, \
            f"В выводе команды get отсутствует фамилия кандидата {candidate.first_name} {candidate.last_name}.\n" \
            f"Вывод команды:\n{get_result.stdout}"


@then(u'данные кандидата соответствуют введенным данным')
def step_impl(context):
    # Проверяем, что данные каждого кандидата соответствуют введенным
    for expected_and_result in context.expected_candidates:
        expected_candidate = expected_and_result[0]
        registration_result = expected_and_result[1]
        
        # Извлекаем ID из результата регистрации
        id_pattern = r'с ID:\s*(\d+)'
        match = re.search(id_pattern, registration_result.stdout)
        
        assert match is not None, \
            f"Не удалось найти ID для проверки данных кандидата {expected_candidate.first_name} {expected_candidate.last_name}"
        
        candidate_id = int(match.group(1))
        
        # Получаем информацию о кандидате через команду get
        args = CliArgumentBuilder() \
            .add("--id", candidate_id) \
            .build()
        
        get_result = context.sut.execute("get", args)
        
        assert get_result.success is True, \
            f"Не удалось получить данные кандидата {expected_candidate.first_name} {expected_candidate.last_name}.\n" \
            f"{get_result.get_error_message()}"
        
        output = get_result.stdout
        
        # Проверяем имя
        actual_first_name = extract_field_from_output(output, "Имя")
        assert actual_first_name == expected_candidate.first_name, \
            f"Имя кандидата не совпадает. Ожидалось: '{expected_candidate.first_name}', получено: '{actual_first_name}'"
        
        # Проверяем фамилию
        actual_last_name = extract_field_from_output(output, "Фамилия")
        assert actual_last_name == expected_candidate.last_name, \
            f"Фамилия кандидата не совпадает. Ожидалось: '{expected_candidate.last_name}', получено: '{actual_last_name}'"
        
        # Проверяем телефон
        if expected_candidate.phone:
            actual_phone = extract_field_from_output(output, "Телефон")
            assert actual_phone == expected_candidate.phone, \
                f"Телефон кандидата не совпадает. Ожидалось: '{expected_candidate.phone}', получено: '{actual_phone}'"
        else:
            # Если телефон не был указан, проверяем, что его нет в выводе
            phone_match = re.search(r'Телефон:', output)
            assert phone_match is None, \
                f"Телефон не должен быть указан для кандидата {expected_candidate.first_name} {expected_candidate.last_name}, " \
                f"но найден в выводе"
        
        # Проверяем дату рождения
        if expected_candidate.birth_date:
            actual_birth_date_str = extract_field_from_output(output, "Дата рождения")
            assert actual_birth_date_str is not None, \
                f"Дата рождения не найдена в выводе для кандидата {expected_candidate.first_name} {expected_candidate.last_name}"
            expected_birth_date_str = expected_candidate.birth_date.strftime("%Y-%m-%d")
            assert actual_birth_date_str == expected_birth_date_str, \
                f"Дата рождения не совпадает. Ожидалось: '{expected_birth_date_str}', получено: '{actual_birth_date_str}'"
        else:
            # Если дата рождения не была указана, проверяем, что ее нет в выводе
            birth_date_match = re.search(r'Дата рождения:', output)
            assert birth_date_match is None, \
                f"Дата рождения не должна быть указана для кандидата {expected_candidate.first_name} {expected_candidate.last_name}, " \
                f"но найдена в выводе"
        
        # Проверяем пол
        if expected_candidate.sex:
            actual_sex = extract_sex_from_output(output)
            expected_sex_value = "M" if expected_candidate.sex.value == 1 else "F"
            assert actual_sex == expected_sex_value, \
                f"Пол кандидата не совпадает. Ожидалось: '{expected_sex_value}', получено: '{actual_sex}'"
        else:
            # Если пол не был указан, проверяем, что его нет в выводе
            sex_match = re.search(r'Пол:', output)
            assert sex_match is None, \
                f"Пол не должен быть указан для кандидата {expected_candidate.first_name} {expected_candidate.last_name}, " \
                f"но найден в выводе"
        
        # Проверяем комментарии
        if expected_candidate.comments:
            actual_comments = extract_field_from_output(output, "Комментарии")
            assert actual_comments == expected_candidate.comments, \
                f"Комментарии не совпадают. Ожидалось: '{expected_candidate.comments}', получено: '{actual_comments}'"
        else:
            # Если комментарии не были указаны, проверяем, что их нет в выводе
            comments_match = re.search(r'Комментарии:', output)
            assert comments_match is None, \
                f"Комментарии не должны быть указаны для кандидата {expected_candidate.first_name} {expected_candidate.last_name}, " \
                f"но найдены в выводе"