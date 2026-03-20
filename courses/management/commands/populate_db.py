from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from courses.models import Category, Course, Grade, Lesson, Book
from users.models import Profile


class Command(BaseCommand):
    help = "Заполняет базу тестовыми пользователями и полноценным контентом Junior/Pro"

    def _upsert_lesson(self, course, order, title, content, video_url=""):
        Lesson.objects.update_or_create(
            course=course,
            order=order,
            defaults={
                "title": title,
                "content": content.strip(),
                "video_url": video_url,
            },
        )

    def handle(self, *args, **options):
        self.stdout.write("Начинаем добавление тестовых данных...")

        # 1. Создаём категории
        categories_data = [
            {"name": "Python"},
        ]
        categories = {}
        for cat_data in categories_data:
            cat, created = Category.objects.get_or_create(name=cat_data["name"])
            categories[cat_data["name"]] = cat
            if created:
                self.stdout.write(self.style.SUCCESS(f"Категория {cat_data['name']} создана"))

        # 2. Создаём преподавателя
        teacher, created = User.objects.get_or_create(
            username="teacher",
            defaults={
                "email": "teacher@example.com",
                "first_name": "Иван",
                "last_name": "Преподаватель",
            }
        )
        if created:
            teacher.set_password("teacher123")
            teacher.save()
        teacher_profile, _ = Profile.objects.get_or_create(
            user=teacher,
            defaults={"role": "teacher"}
        )
        if teacher_profile.role != "teacher":
            teacher_profile.role = "teacher"
            teacher_profile.save(update_fields=["role"])
        if created:
            self.stdout.write(self.style.SUCCESS(f"Преподаватель '{teacher.username}' создан"))

        # 3. Создаём студентов
        students_data = [
            {"username": "student1", "email": "student1@example.com", "first_name": "Александр", "last_name": "Иванов"},
            {"username": "student2", "email": "student2@example.com", "first_name": "Мария", "last_name": "Петрова"},
            {"username": "student3", "email": "student3@example.com", "first_name": "Дмитрий", "last_name": "Сидоров"},
            {"username": "student4", "email": "student4@example.com", "first_name": "Екатерина", "last_name": "Кузнецова"},
            {"username": "student5", "email": "student5@example.com", "first_name": "Павел", "last_name": "Смирнов"},
        ]
        students = []
        for student_data in students_data:
            student, created = User.objects.get_or_create(
                username=student_data["username"],
                defaults={
                    "email": student_data["email"],
                    "first_name": student_data["first_name"],
                    "last_name": student_data["last_name"],
                }
            )
            if created:
                student.set_password("student123")
                student.save()
            profile, _ = Profile.objects.get_or_create(
                user=student,
                defaults={"role": "student"}
            )
            students.append(student)
            if created:
                self.stdout.write(self.style.SUCCESS(f"✓ Студент '{student.username}' создан"))

        # 4. Создаём 2 ключевых курса для запуска
        courses_data = [
            {
                "title": "Python для начинающих",
                "description": (
                    "База Python с нуля: синтаксис, условия, циклы, функции, "
                    "коллекции и мини-проекты."
                ),
                "category": "Python",
                "level": "junior",
                "price": 0,
            },
            {
                "title": "Python для профессионалов",
                "description": (
                    "Продвинутый Python: архитектура, Flask, Django, API, "
                    "тесты и деплой."
                ),
                "category": "Python",
                "level": "pro",
                "price": 4,
            },
        ]
        courses = {}
        for course_data in courses_data:
            course, created = Course.objects.update_or_create(
                title=course_data["title"],
                defaults={
                    "description": course_data["description"],
                    "category": categories[course_data["category"]],
                    "level": course_data["level"],
                    "author": teacher,
                    "price": course_data["price"],
                    "is_active": True,
                }
            )
            courses[course_data["title"]] = course
            if created:
                self.stdout.write(self.style.SUCCESS(f"✓ Курс '{course.title}' создан"))
            else:
                self.stdout.write(self.style.SUCCESS(f"✓ Курс '{course.title}' обновлён"))

        # 5. Заполняем уроки Junior
        junior = courses["Python для начинающих"]
        junior_lessons = [
            (
                1,
                "Модуль 1. Старт: установка, переменные, типы",
                """
# Модуль 1: Старт в Python

## Теория
- Установка Python и запуск в терминале
- `print()`, переменные, числа, строки, `bool`
- Базовый стиль кода (PEP8)

## Практика
1. Создай файл `hello.py`
2. Выведи имя, возраст и город
3. Посчитай сумму и среднее двух чисел

## Домашка
- Сделай мини-визитку в консоли (5-7 строк вывода)
- Добавь комментарии к каждой важной строке
                """,
            ),
            (
                2,
                "Модуль 1. Условия и ветвления",
                """
# Модуль 1: Условия

## Теория
- Операторы сравнения
- `if / elif / else`
- Логические операторы `and`, `or`, `not`

## Практика
1. Проверка совершеннолетия
2. Калькулятор скидки по сумме заказа
3. Проверка пароля по длине

## Домашка
- Напиши программу «Оценка по баллам»
- Добавь обработку неверного ввода
                """,
            ),
            (
                3,
                "Модуль 2. Циклы и списки",
                """
# Модуль 2: Циклы и списки

## Теория
- `for` и `while`
- Списки: добавление, удаление, срезы
- `range()`, `enumerate()`

## Практика
1. Вывести таблицу умножения на 7
2. Найти максимум в списке без `max()`
3. Посчитать средний балл группы

## Домашка
- Игра «Угадай число»
- Сохрани историю попыток в списке и выведи после победы
                """,
            ),
            (
                4,
                "Модуль 2. Функции и декомпозиция",
                """
# Модуль 2: Функции

## Теория
- Зачем нужны функции
- Параметры, `return`
- Области видимости

## Практика
1. Функция подсчёта НДС
2. Функция проверки палиндрома
3. Разделение большого скрипта на 3 функции

## Домашка
- Собери консольный мини-проект «Трекер расходов»
- Вынеси ввод, расчёты и отчёт в отдельные функции
                """,
            ),
            (
                5,
                "Модуль 3. Словари, файлы и мини-проект",
                """
# Модуль 3: Словари и файлы

## Теория
- Словари: ключи и значения
- Чтение/запись файлов
- Структура небольшого проекта

## Практика
1. Телефонная книга на словаре
2. Сохранение данных в `.txt`
3. Загрузка данных при старте

## Домашка
- Финальный проект Junior: «Менеджер задач в консоли»
- Требования: добавить, удалить, отметить выполненным, сохранить в файл
                """,
            ),
        ]
        for order, title, content in junior_lessons:
            self._upsert_lesson(junior, order, title, content)

        # 6. Заполняем уроки Pro
        pro = courses["Python для профессионалов"]
        pro_lessons = [
            (
                1,
                "Модуль 1. Архитектура и чистый Python",
                """
# Модуль 1: Архитектура

## Теория
- Структура production-проекта
- Виртуальные окружения, зависимости
- Логирование и конфиги

## Практика
1. Разбей проект на `services`, `repositories`, `api`
2. Добавь `logging` с ротацией
3. Настрой `.env` и валидацию переменных

## Домашка
- Рефакторинг существующего скрипта в модульную структуру
                """,
            ),
            (
                2,
                "Модуль 1. Flask API: CRUD и валидация",
                """
# Модуль 1: Flask API

## Теория
- REST, маршруты, статусы ответов
- Валидация входных данных
- Обработка ошибок

## Практика
1. CRUD для сущности `Task`
2. Проверка полей запроса
3. Единый формат JSON-ошибок

## Домашка
- Добавить пагинацию и фильтрацию по статусу
                """,
            ),
            (
                3,
                "Модуль 2. Django: модели, ORM, админка",
                """
# Модуль 2: Django Core

## Теория
- Модели и миграции
- Связи `FK/M2M/OneToOne`
- Кастомизация админки

## Практика
1. Модели для учебной платформы
2. Нормальные индексы и `select_related`
3. Админка для контент-менеджера

## Домашка
- Спроектировать ER-диаграмму и реализовать миграции
                """,
            ),
            (
                4,
                "Модуль 2. Django REST + авторизация",
                """
# Модуль 2: DRF и Auth

## Теория
- Сериализаторы и ViewSet
- Permissions
- JWT/session авторизация

## Практика
1. Endpoint списка уроков
2. Закрытие платных endpoint по роли/доступу
3. Тесты на авторизацию

## Домашка
- Добавить endpoint прогресса по урокам
                """,
            ),
            (
                5,
                "Модуль 3. Тесты, CI и деплой на Render",
                """
# Модуль 3: Продакшен

## Теория
- Unit/integration тесты
- Подготовка проекта к контейнерному деплою
- Работа с Postgres и переменными окружения

## Практика
1. Тесты на ключевые сценарии оплаты и доступа
2. Подключение Postgres через `DATABASE_URL`
3. Настройка статики и миграций на старте

## Домашка
- Итоговый мини-проект: задеплоить API и дать публичный URL
                """,
            ),
        ]
        for order, title, content in pro_lessons:
            self._upsert_lesson(pro, order, title, content)

        # 7. Рекомендуемые книги
        books_map = {
            "Python для начинающих": [
                ("Automate the Boring Stuff with Python", "https://automatetheboringstuff.com"),
                ("Python Crash Course", "https://nostarch.com/pythoncrashcourse2e"),
            ],
            "Python для профессионалов": [
                ("Two Scoops of Django", "https://www.feldroy.com/books/two-scoops-of-django-3-x"),
                ("Architecture Patterns with Python", "https://www.cosmicpython.com"),
            ],
        }
        for course_title, books in books_map.items():
            course = courses[course_title]
            for idx, (title, url) in enumerate(books, start=1):
                Book.objects.update_or_create(
                    course=course,
                    title=title,
                    defaults={"url": url, "order": idx},
                )

        # 8. Создаём оценки по двум ключевым курсам
        junior = courses["Python для начинающих"]
        pro = courses["Python для профессионалов"]
        grades_data = [
            {"student": students[0], "course": junior, "grade": 5},
            {"student": students[0], "course": pro, "grade": 4},
            {"student": students[1], "course": junior, "grade": 4},
            {"student": students[2], "course": pro, "grade": 3},
            {"student": students[3], "course": junior, "grade": 5},
            {"student": students[4], "course": pro, "grade": 4},
        ]
        for grade_data in grades_data:
            grade, created = Grade.objects.get_or_create(
                student=grade_data["student"],
                course=grade_data["course"],
                defaults={"grade": grade_data["grade"]}
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Оценка: {grade.student.username} → {grade.course.title} = {grade.grade}/5"
                    )
                )

        self.stdout.write(self.style.SUCCESS("\nКонтент Junior/Pro успешно подготовлен."))
        self.stdout.write("\n📋 Учётные данные для входа:")
        self.stdout.write("─" * 50)
        self.stdout.write(self.style.WARNING("Преподаватель:"))
        self.stdout.write(f"  Логин: teacher")
        self.stdout.write(f"  Пароль: teacher123")
        self.stdout.write("")
        self.stdout.write(self.style.WARNING("Студенты:"))
        self.stdout.write(f"  Логин: student1-5")
        self.stdout.write(f"  Пароль: student123")
        self.stdout.write("─" * 50)
