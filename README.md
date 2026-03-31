# DevLearn

Платформа для изучения программирования (Python, курсы, уроки, сертификаты).  
Piattaforma per l’apprendimento della programmazione (Python, corsi, lezioni, certificati).

---

## Русский

### Зависимости (`requirements.txt`)

Все пакеты перечислены в **`requirements.txt`**. Основные:

| Назначение | Пакеты |
|------------|--------|
| Фреймворк | `Django` 5.2.x |
| Медиа, изображения | `Pillow` |
| Контент уроков | `markdown`, `django-markdownx` |
| Конфигурация | `python-dotenv` |
| API | `djangorestframework` |
| AI на уроке | `groq` |
| Оплата | `stripe` |
| PDF-сертификаты | `reportlab` |
| Облако для медиа (опционально) | `django-cloudinary-storage` |
| Продакшен (Render и т.п.) | `gunicorn`, `whitenoise`, `dj-database-url`, `psycopg2-binary` |

Установка: **`pip install -r requirements.txt`** (из активированного виртуального окружения).

### Стек

- Python **3.12+**
- Django **5.2**
- SQLite (локально) / PostgreSQL через `DATABASE_URL` (например, Render)

### Быстрый старт

1. Клонировать репозиторий и перейти в каталог:
   ```bash
   git clone https://github.com/Mikulskaya96/django_project1.git
   cd django_project1
   ```

2. Виртуальное окружение и активация:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```
   Linux/macOS: `source .venv/bin/activate`

3. Установить зависимости (**обязательно**):
   ```bash
   pip install -r requirements.txt
   ```

4. Переменные окружения:
   ```bash
   copy .env.example .env
   ```
   (Linux/macOS: `cp .env.example .env`)  
   При необходимости отредактируйте `.env`. Для продакшена задайте `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=False`.  
   Для AI-блока на уроке: **`GROQ_API_KEY`** (и при необходимости `GEMINI_API_KEY` — см. `settings.py`).  
   Для Stripe, Cloudinary — см. комментарии в `.env.example`.

5. Миграции и (по желанию) данные:
   ```bash
   python manage.py migrate
   python manage.py populate_db
   ```

6. Суперпользователь (доступ в `/admin/`):
   ```bash
   python manage.py createsuperuser
   ```

7. Запуск:
   ```bash
   python manage.py runserver
   ```
   Сайт: http://127.0.0.1:8000/ — админка: http://127.0.0.1:8000/admin/

### Тесты

```bash
python manage.py test
```

При push в ветки `main` / `master` в репозитории настроен **GitHub Actions** (см. `.github/workflows/`).

### Деплой на Render (кратко)

Репозиторий на GitHub → сервис на [render.com](https://render.com), переменные окружения (`DJANGO_SECRET_KEY`, `DATABASE_URL`, при необходимости `GROQ_API_KEY`, Stripe, `CLOUDINARY_URL`, суперпользователь для сборки и т.д.). Подробности — в настройках вашего сервиса и в `render.yaml`, если используется.

### Структура проекта

- `main` — главная, статические страницы (о нас, контакты, оферта)
- `users` — регистрация, вход, профили (роли студент / преподаватель)
- `courses` — курсы, уроки, записи, API `/api/`, сертификаты PDF
- `settings` — конфигурация Django

---

## Italiano

### Dipendenze (`requirements.txt`)

Tutti i pacchetti sono elencati in **`requirements.txt`**. Esempi:

| Uso | Pacchetti |
|-----|-----------|
| Framework | `Django` 5.2.x |
| Immagini | `Pillow` |
| Contenuti lezioni | `markdown`, `django-markdownx` |
| Configurazione | `python-dotenv` |
| API REST | `djangorestframework` |
| Assistente AI sulla lezione | `groq` |
| Pagamenti | `stripe` |
| Certificati PDF | `reportlab` |
| Media cloud (opzionale) | `django-cloudinary-storage` |
| Produzione (Render ecc.) | `gunicorn`, `whitenoise`, `dj-database-url`, `psycopg2-binary` |

Installazione: **`pip install -r requirements.txt`** (con ambiente virtuale attivo).

### Stack

- Python **3.12+**
- Django **5.2**
- SQLite (locale) / PostgreSQL tramite `DATABASE_URL` (es. su Render)

### Avvio rapido

1. Clona il repository e entra nella cartella:
   ```bash
   git clone https://github.com/Mikulskaya96/django_project1.git
   cd django_project1
   ```

2. Ambiente virtuale:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```
   Linux/macOS: `source .venv/bin/activate`

3. Installa le dipendenze (**obbligatorio**):
   ```bash
   pip install -r requirements.txt
   ```

4. Variabili d’ambiente:
   ```bash
   copy .env.example .env
   ```
   (Linux/macOS: `cp .env.example .env`)  
   Modifica `.env` se serve. In produzione: `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=False`.  
   Per l’AI sulla lezione: **`GROQ_API_KEY`**. Stripe e Cloudinary: vedi `.env.example`.

5. Migrazioni e (opzionale) dati di esempio:
   ```bash
   python manage.py migrate
   python manage.py populate_db
   ```

6. Superuser (admin `/admin/`):
   ```bash
   python manage.py createsuperuser
   ```

7. Avvio server di sviluppo:
   ```bash
   python manage.py runserver
   ```
   Sito: http://127.0.0.1:8000/ — admin: http://127.0.0.1:8000/admin/

### Test

```bash
python manage.py test
```

### Licenza / License

MIT (o indicare la propria).
