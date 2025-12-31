# HR Management System

Демонстрационное консольное приложение для управления кандидатами в HR системе.

## Описание

HR Management System - это CLI приложение на Python для регистрации и управления кандидатами. Приложение использует SQLite для хранения данных и предоставляет удобный интерфейс командной строки с поддержкой интерактивного режима.

## Требования

- Python 3.8 или выше
- pip (менеджер пакетов Python)

## Установка

### Установка из GitHub Releases

Скачайте wheel файл из [последнего релиза](https://github.com/andreykarinskiy/FSB.Application.HRM/releases/latest) и установите через pip:

```bash
pip install https://github.com/andreykarinskiy/FSB.Application.HRM/releases/download/v0.1.0/esb_application_hrm-0.1.0-py3-none-any.whl
```

Или для установки в пользовательскую директорию (без прав администратора):

```bash
pip install --user https://github.com/andreykarinskiy/FSB.Application.HRM/releases/download/v0.1.0/esb_application_hrm-0.1.0-py3-none-any.whl
```

**Примечание:** После установки с флагом `--user` убедитесь, что `~/.local/bin` (Linux/macOS) или `%APPDATA%\Python\Python<версия>\Scripts` (Windows) добавлен в переменную окружения PATH.

### Установка конкретной версии

Замените `v0.1.0` на нужную версию в URL выше.

## Docker

Приложение доступно в виде Docker образа в GitHub Container Registry (GHCR).

### Использование Docker образа

#### Запуск через docker run

```bash
# Показать справку
docker run --rm ghcr.io/andreykarinskiy/esb-application-hrm:latest --help

# Показать список кандидатов
docker run --rm \
  -v hrm-data:/app/data \
  -e HRM_DB_PATH=/app/data/candidates.db \
  ghcr.io/andreykarinskiy/esb-application-hrm:latest list

# Добавить кандидата
docker run --rm -it \
  -v hrm-data:/app/data \
  -e HRM_DB_PATH=/app/data/candidates.db \
  ghcr.io/andreykarinskiy/esb-application-hrm:latest add \
  --first-name "Иван" --last-name "Иванов" \
  --phone "+7-999-123-45-67" --birth-date "1990-01-15" --sex "M"

# Использовать локальную директорию для базы данных
docker run --rm \
  -v $(pwd)/data:/app/data \
  -e HRM_DB_PATH=/app/data/candidates.db \
  ghcr.io/andreykarinskiy/esb-application-hrm:latest list
```

**Доступные теги:**
- `latest` - последняя версия из ветки main
- `develop` - последняя версия из ветки develop
- `v*` - конкретные версии (например, `v0.1.1`)

#### Использование docker-compose

1. Создайте файл `docker-compose.yml` (уже включен в проект) или используйте существующий.

2. Запустите команду:

```bash
# Показать справку (по умолчанию)
docker-compose run --rm hrm

# Показать список кандидатов
docker-compose run --rm hrm list

# Добавить кандидата
docker-compose run --rm hrm add \
  --first-name "Иван" --last-name "Иванов" \
  --phone "+7-999-123-45-67" --birth-date "1990-01-15" --sex "M"

# Интерактивный режим
docker-compose run --rm hrm add-interactive
```

3. Данные сохраняются в Docker volume `hrm-data`. Для использования локальной директории измените `docker-compose.yml`:

```yaml
volumes:
  # - hrm-data:/app/data  # Закомментируйте эту строку
  - ./data:/app/data      # Раскомментируйте эту строку
```

**Доступ к образу в GHCR:**
- [ghcr.io/andreykarinskiy/esb-application-hrm](https://github.com/andreykarinskiy/ESB.Application.HRM/pkgs/container/esb-application-hrm)

### Переменные окружения

- `HRM_DB_PATH` - путь к файлу базы данных SQLite (по умолчанию: `~/.hrm/candidates.db`)

## Запуск

После установки приложение доступно через команду `hrm`:

```bash
hrm --help
```

## Основные команды

### Регистрация кандидата

**Командная строка:**
```bash
hrm add --first-name "Иван" --last-name "Иванов" --phone "+7-999-123-45-67" --birth-date "1990-01-15" --sex "M"
```

**Интерактивный режим:**
```bash
hrm add-interactive
```

### Просмотр списка кандидатов

```bash
hrm list
```

### Получение информации о кандидате

```bash
hrm get --id 1
```

### Редактирование кандидата

**Командная строка:**
```bash
hrm edit --id 1 --first-name "Петр" --phone "+7-999-765-43-21"
```

**Интерактивный режим:**
```bash
hrm edit-interactive
```

### Удаление кандидата

```bash
hrm delete --id 1
```

Или без подтверждения:
```bash
hrm delete --id 1 --force
```

### Очистка репозитория

```bash
hrm clear
```

Или без подтверждения:
```bash
hrm clear --force
```

## Параметры команд

### add / edit

- `--first-name`, `-f` - Имя кандидата (обязательно для add)
- `--last-name`, `-l` - Фамилия кандидата (обязательно для add)
- `--phone`, `-p` - Контактный телефон (необязательно)
- `--birth-date`, `-b` - Дата рождения в формате YYYY-MM-DD (необязательно)
- `--sex`, `-s` - Пол: M (мужской) или F (женский) (необязательно)
- `--comments`, `-c` - Комментарии (необязательно)

### get / delete

- `--id`, `-i` - ID кандидата (обязательно)

## Примеры использования

### Регистрация нового кандидата

```bash
hrm add --first-name "Анна" --last-name "Петрова" --phone "+7-999-111-22-33" --birth-date "1995-05-20" --sex "F" --comments "Опыт работы 3 года"
```

### Просмотр всех кандидатов

```bash
hrm list
```

### Изменение телефона кандидата

```bash
hrm edit --id 1 --phone "+7-999-999-99-99"
```

## Хранение данных

Приложение использует SQLite базу данных, которая создается автоматически при первом запуске. 

По умолчанию база данных хранится в файле `~/.hrm/candidates.db`. Путь к базе данных можно изменить через переменную окружения `HRM_DB_PATH`:

```bash
export HRM_DB_PATH=/path/to/your/database.db
hrm list
```

В Docker контейнере по умолчанию используется путь `/app/data/candidates.db`, который можно настроить через переменную окружения `HRM_DB_PATH`.

## Технологический стек

- **typer** - создание CLI интерфейса
- **rich** - форматированный вывод в консоль
- **sqlalchemy** - работа с базой данных
- **pydantic** - валидация данных
- **sqlite** - база данных

## Разработка

Для разработки установите зависимости разработки:

```bash
pip install -e ".[dev]"
```

Запуск тестов:

```bash
# Приемочные тесты
behave tests/acceptance
```

## Лицензия

Демонстрационное приложение для образовательных целей.
