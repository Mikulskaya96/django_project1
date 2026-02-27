# DevLearn

Платформа для обучения программированию на Django.

## Стек

- Python 3.12+
- Django 5.2
- SQLite (разработка) / возможность перехода на PostgreSQL

## Быстрый старт

1. Клонировать репозиторий и перейти в папку проекта:
   ```bash
   git clone https://github.com/ВАШ_ЛОГИН/django_project1.git
   cd django_project1
   ```

2. Создать виртуальное окружение и активировать его:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```
   (Linux/macOS: `source .venv/bin/activate`)

3. Установить зависимости:
   ```bash
   pip install -r requirements.txt
   ```

4. Настроить переменные окружения (опционально для разработки):
   ```bash
   cp .env.example .env
   ```
   Отредактируйте `.env` при необходимости. Для продакшена обязательно задайте `DJANGO_SECRET_KEY` и `DJANGO_DEBUG=False`.

5. Применить миграции:
   ```bash
   python manage.py migrate
   ```

6. (Опционально) Создать суперпользователя для доступа в админку:
   ```bash
   python manage.py createsuperuser
   ```

7. Запустить сервер:
   ```bash
   python manage.py runserver
   ```

8. Открыть в браузере: http://127.0.0.1:8000/  
   Админка: http://127.0.0.1:8000/admin/

## Тестирование

```bash
python manage.py test
```

В репозитории настроен GitHub Actions: при push в `main`/`master` автоматически запускаются тесты.

## Структура проекта

- `main` — главная страница
- `users` — регистрация, вход, профили (роли: студент/преподаватель)
- `courses` — курсы, уроки, записи студентов, журнал оценок
- `settings` — конфигурация Django

## Лицензия

MIT (или укажите свою).
