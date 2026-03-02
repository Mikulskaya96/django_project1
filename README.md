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

## Деплой на Render

1. Залей проект в **GitHub** (если ещё не залит).
2. Зайди на [render.com](https://render.com), зарегистрируйся (можно через GitHub).
3. **Dashboard** → **New** → **Blueprint**. Укажи репозиторий и ветку (например `main`). Render подхватит `render.yaml` из корня.
4. После создания сервиса открой **Environment** и добавь вручную:
   - `GEMINI_API_KEY` — твой ключ из [Google AI Studio](https://aistudio.google.com/apikey) (чтобы работал блок «Спросить ИИ»).
5. Дождись окончания деплоя. Сайт будет доступен по ссылке вида `https://devlearn.onrender.com`.
6. **Суперпользователь:** в Dashboard открой вкладку **Shell** и выполни:
   ```bash
   python manage.py createsuperuser
   ```
   Введи логин, email и пароль — после этого можно заходить в админку на продакшене.

На бесплатном тарифе сервис «засыпает» после ~15 минут без заходов; первый запрос после сна может открываться 30–60 секунд.

## Структура проекта

- `main` — главная страница
- `users` — регистрация, вход, профили (роли: студент/преподаватель)
- `courses` — курсы, уроки, записи студентов, журнал оценок
- `settings` — конфигурация Django

## Лицензия

MIT (или укажите свою).
