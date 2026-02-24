# DevLearn

Платформа для обучения программированию (Django).

## Как запустить

1. Клонировать репозиторий и перейти в папку проекта.
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
4. Применить миграции:
   ```bash
   python manage.py migrate
   ```
5. (Опционально) Создать суперпользователя для доступа в админку:
   ```bash
   python manage.py createsuperuser
   ```
6. Запустить сервер:
   ```bash
   python manage.py runserver
   ```
7. Открыть в браузере: http://127.0.0.1:8000/

Админка: http://127.0.0.1:8000/admin/
