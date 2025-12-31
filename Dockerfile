FROM python:3.12-slim

# Метаданные для GHCR
LABEL org.opencontainers.image.title="HR Management System"
LABEL org.opencontainers.image.description="Демонстрационное консольное приложение для управления кандидатами в HR системе"
LABEL org.opencontainers.image.vendor="HR Management System"
LABEL maintainer="HR Management System"

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копирование файлов зависимостей для улучшения кэширования
COPY pyproject.toml ./
COPY README.md ./

# Установка зависимостей Python (кэшируется, если pyproject.toml не изменился)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e .

# Копирование исходного кода (отдельный слой для кэширования)
COPY src/ ./src/

# Создание директории для базы данных
RUN mkdir -p /app/data

# Переменная окружения для пути к БД
ENV HRM_DB_PATH=/app/data/candidates.db

# Точка входа - используем команду hrm
ENTRYPOINT ["hrm"]
