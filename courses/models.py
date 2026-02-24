from django.db import models
from django.conf import settings


class Category(models.Model):
    """Категория курсов (Python, JavaScript, Django и т.д.)."""

    name = models.CharField("Название", max_length=50)

    def __str__(self):
        return self.name


class Course(models.Model):
    """Курс. author — кто создал; price можно сделать 0 для бесплатных."""

    title = models.CharField("Название", max_length=50)
    description = models.TextField("Описание", blank=True)
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
    price = models.DecimalField(
        "Цена",
        max_digits=10,
        decimal_places=2,
        default=0,
    )
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
    title = models.CharField("Название", max_length=50)
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
    title = models.CharField("Название", max_length=50)
    content = models.TextField("Содержание (Markdown)", blank=True)
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
