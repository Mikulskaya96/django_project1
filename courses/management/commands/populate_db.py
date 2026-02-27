from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from courses.models import Category, Course, Grade
from users.models import Profile


class Command(BaseCommand):
    help = "Добавляет тестовые данные: студентов, курсы и оценки"

    def handle(self, *args, **options):
        self.stdout.write("🚀 Начинаем добавление тестовых данных...")

        # 1. Создаём категории
        categories_data = [
            {"name": "Python"},
            {"name": "JavaScript"},
            {"name": "Django"},
            {"name": "React"},
        ]
        categories = {}
        for cat_data in categories_data:
            cat, created = Category.objects.get_or_create(name=cat_data["name"])
            categories[cat_data["name"]] = cat
            if created:
                self.stdout.write(self.style.SUCCESS(f"✓ Категория {cat_data['name']} создана"))

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
        if created:
            self.stdout.write(self.style.SUCCESS(f"✓ Преподаватель '{teacher.username}' создан"))

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

        # 4. Создаём курсы
        courses_data = [
            {
                "title": "Python для начинающих",
                "description": "Основы программирования на Python",
                "category": "Python",
                "price": 0,
            },
            {
                "title": "Django REST API",
                "description": "Создание API с Django REST Framework",
                "category": "Django",
                "price": 50,
            },
            {
                "title": "JavaScript Basics",
                "description": "Введение в JavaScript",
                "category": "JavaScript",
                "price": 20,
            },
            {
                "title": "React для профессионалов",
                "description": "Продвинутые техники работы с React",
                "category": "React",
                "price": 100,
            },
        ]
        courses = []
        for course_data in courses_data:
            course, created = Course.objects.get_or_create(
                title=course_data["title"],
                defaults={
                    "description": course_data["description"],
                    "category": categories[course_data["category"]],
                    "author": teacher,
                    "price": course_data["price"],
                }
            )
            courses.append(course)
            if created:
                self.stdout.write(self.style.SUCCESS(f"✓ Курс '{course.title}' создан"))

        # 5. Создаём оценки
        grades_data = [
            {"student": students[0], "course": courses[0], "grade": 5},
            {"student": students[0], "course": courses[1], "grade": 4},
            {"student": students[1], "course": courses[0], "grade": 4},
            {"student": students[1], "course": courses[2], "grade": 5},
            {"student": students[2], "course": courses[1], "grade": 3},
            {"student": students[2], "course": courses[3], "grade": 2},
            {"student": students[3], "course": courses[0], "grade": 5},
            {"student": students[3], "course": courses[2], "grade": 5},
            {"student": students[4], "course": courses[2], "grade": 4},
            {"student": students[4], "course": courses[3], "grade": 5},
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

        self.stdout.write(self.style.SUCCESS("\n✨ Все тестовые данные успешно добавлены!"))
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
