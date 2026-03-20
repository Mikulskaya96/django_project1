from django.db import models
from django.conf import settings
from markdownx.models import MarkdownxField
import uuid


class Category(models.Model):
    """Категория курсов (Python, JavaScript, Django и т.д.)."""

    name = models.CharField("Название", max_length=100)

    def __str__(self):
        return self.name


class Course(models.Model):
    """Курс. author — кто создал; price можно сделать 0 для бесплатных."""
    
    LEVEL_JUNIOR = "junior"
    LEVEL_PRO = "pro"
    LEVEL_CHOICES = [
        (LEVEL_JUNIOR, "Python для начинающих"),
        (LEVEL_PRO, "Python для профессионалов"),
    ]

    title = models.CharField("Название", max_length=100)
    description = models.TextField("Описание", blank=True)
    level = models.CharField(
        "Уровень",
        max_length=20,
        choices=LEVEL_CHOICES,
        default=LEVEL_JUNIOR,
    )
    category = models.ForeignKey(
        "Category",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="courses",
        verbose_name="Категория",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="authored_courses",
        verbose_name="Автор",
    )
    cover_image = models.ImageField(
        "Обложка курса",
        upload_to="courses/covers/",
        blank=True,
        null=True,
    )
    price = models.DecimalField(
        "Цена",
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    is_active = models.BooleanField("Опубликован", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Book(models.Model):
    """Книга по курсу — ссылка на рекомендуемую литературу."""

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="books",
        verbose_name="Курс",
    )
    title = models.CharField("Название", max_length=100)
    url = models.URLField("Ссылка")
    order = models.PositiveIntegerField("Порядок", default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.course.title} — {self.title}"


class Lesson(models.Model):
    """Урок курса. content — Markdown, video_url — ссылка на видео."""

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name="Курс",
    )
    title = models.CharField("Название", max_length=100)
    content = MarkdownxField("Содержание", blank=True)
    image = models.ImageField(
        "Картинка урока",
        upload_to="courses/lessons/",
        blank=True,
        null=True,
    )
    video_url = models.URLField("Ссылка на видео", blank=True)
    order = models.PositiveIntegerField("Порядок", default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.course.title} — {self.title}"


class Enrollment(models.Model):
    """Запись на курс. Если запись есть — студент имеет доступ к урокам."""

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="enrollments",
        verbose_name="Студент",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="enrollments",
        verbose_name="Курс",
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["student", "course"]

    def __str__(self):
        return f"{self.student.username} → {self.course.title}"


class LessonProgress(models.Model):
    """Прогресс по уроку — отметка «пройден»."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lesson_progress",
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="progress",
    )
    completed_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["user", "lesson"]


class LessonAiMessage(models.Model):
    """Сообщение диалога с ИИ по конкретному уроку."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lesson_ai_messages",
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="ai_messages",
    )
    question = models.TextField("Вопрос")
    answer = models.TextField("Ответ", blank=True)
    created_at = models.DateTimeField("Время", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

class Grade(models.Model):
    """Оценка студента по курсу. Содержит оценку и дату."""

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="grades",
        verbose_name="Студент",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="grades",
        verbose_name="Курс",
    )
    grade = models.IntegerField(
        "Оценка",
        choices=[(i, str(i)) for i in range(1, 6)],
        default=1,
    )
    date = models.DateTimeField("Дата оценки", auto_now=True)

    class Meta:
        unique_together = ["student", "course"]
        ordering = ["-date"]

    def __str__(self):
        return f"{self.student.username} — {self.course.title}: {self.grade}"


class CourseCertificate(models.Model):
    """Сертификат о завершении курса."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="course_certificates",
        verbose_name="Пользователь",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="certificates",
        verbose_name="Курс",
    )
    certificate_id = models.UUIDField(
        "Идентификатор сертификата",
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )
    issued_at = models.DateTimeField("Дата выдачи", auto_now_add=True)

    class Meta:
        unique_together = ["user", "course"]
        ordering = ["-issued_at"]

    def __str__(self):
        return f"Certificate {self.certificate_id} — {self.user.username}/{self.course.title}"
