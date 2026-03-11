# Dockerfile
FROM python:3.12-slim

# Обновляем пакеты и ставим системные зависимости (для psycopg, Pillow и т.п.)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Рабочая директория внутри контейнера
WORKDIR /app

# Копируем requirements и ставим зависимости
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект внутрь контейнера
COPY . /app/

# Настройки Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Порт, который будет слушать Django
EXPOSE 8000

# Команда по умолчанию (для разработки)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]