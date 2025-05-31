# Базовый образ Python
FROM python:3.10-slim-buster

# Устанавливаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Рабочая директория внутри контейнера
WORKDIR /app

# Установка зависимостей системы (для Pillow и psycopg2)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       libpq-dev \
       gcc \
       libjpeg-dev \
       zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем файл зависимостей и устанавливаем их
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Копируем весь проект в рабочую директорию
COPY . .

# Создаем директории для статики и медиа и даем права (если gunicorn/django будут создавать файлы)
RUN mkdir -p /app/staticfiles /app/mediafiles
# Если ваше приложение будет писать в mediafiles из-под другого пользователя, нужно будет настроить права
# RUN chown -R someuser:somegroup /app/mediafiles 

# Порт, который будет слушать Gunicorn
EXPOSE 8000

# Команда для запуска Gunicorn (для продакшена)
# Для разработки можно использовать `python manage.py runserver 0.0.0.0:8000`
# Но в Docker лучше сразу использовать прод-сервер
# Запуск скрипта entrypoint.sh (см. ниже, опционально, для миграций и т.д.)
# CMD ["gunicorn", "portfolio_platform.wsgi:application", "--bind", "0.0.0.0:8000"]