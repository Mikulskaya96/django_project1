from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from markdownx.models import MarkdownxField


class Category(models.Model):
    """Категория курсов (Python, JavaScript, Django и т.д.)."""

    name = models.CharField(_("Название"), max_length=100)

    class Meta:
        verbose_name = _("Категория")
        verbose_name_plural = _("Категории")

    def __str__(self):
        return self.name


class Course(models.Model):
    """Курс. author — кто создал; price можно сделать 0 для бесплатных."""

    LEVEL_JUNIOR = "junior"
    LEVEL_PRO = "pro"
    LEVEL_CHOICES = [
        (LEVEL_JUNIOR, _("Python для начинающих")),
        (LEVEL_PRO, _("Python для профессионалов")),
    ]

    title = models.CharField(_("Название"), max_length=100)
    description = models.TextField(_("Описание"), blank=True)
    level = models.CharField(
        _("Уровень"),
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
        verbose_name=_("Категория"),
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="authored_courses",
        verbose_name=_("Автор"),
    )
    cover_image = models.ImageField(
        _("Обложка курса"),
        upload_to="courses/covers/",
        blank=True,
        null=True,
        help_text=_(
            "Каталог и страница курса. Если пусто — «Картинка урока»: junior — 2-й по списку; "
            "pro — у урока с полем «Порядок» = 3 (финальный урок с «Слово автора» — отдельно)."
        ),
    )
    author_image = models.ImageField(
        _("Фото автора (блок «Слово автора»)"),
        upload_to="courses/authors/",
        blank=True,
        null=True,
        help_text=_(
            "Показывается в финальном уроке Pro у маркера <!-- AUTHOR_PHOTO -->. "
            "Если не задано — можно использовать «Картинку урока» в том же уроке."
        ),
    )
    price = models.DecimalField(
        _("Цена"),
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    is_active = models.BooleanField(_("Опубликован"), default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Курс")
        verbose_name_plural = _("Курсы")

    def __str__(self):
        return self.title


class Book(models.Model):
    """Книга по курсу — ссылка на рекомендуемую литературу."""

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="books",
        verbose_name=_("Курс"),
    )
    title = models.CharField(_("Название"), max_length=100)
    url = models.URLField(_("Ссылка"))
    order = models.PositiveIntegerField(_("Порядок"), default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = _("Книга")
        verbose_name_plural = _("Книги")

    def __str__(self):
        return f"{self.course.title} — {self.title}"


class Lesson(models.Model):
    """Урок курса. content — Markdown, video_url — ссылка на видео."""

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name=_("Курс"),
    )
    title = models.CharField(_("Название"), max_length=100)
    content = MarkdownxField(_("Содержание"), blank=True)
    image = models.ImageField(
        _("Картинка урока"),
        upload_to="courses/lessons/",
        blank=True,
        null=True,
        help_text=_(
            "Junior: 2-й урок — запасная обложка. Pro: урок с «Порядок» 3 — обложка; финальный урок — "
            "«Слово автора» (<!-- AUTHOR_PHOTO -->). Иначе иллюстрация сверху, если урок не источник обложки."
        ),
    )
    video_url = models.URLField(_("Ссылка на видео"), blank=True)
    order = models.PositiveIntegerField(_("Порядок"), default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = _("Урок")
        verbose_name_plural = _("Уроки")

    def __str__(self):
        return f"{self.course.title} — {self.title}"


class Enrollment(models.Model):
    """Запись на курс. Если запись есть — студент имеет доступ к урокам."""

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="enrollments",
        verbose_name=_("Студент"),
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="enrollments",
        verbose_name=_("Курс"),
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["student", "course"]
        verbose_name = _("Запись на курс")
        verbose_name_plural = _("Записи на курсы")

    def __str__(self):
        return f"{self.student.username} → {self.course.title}"


class LessonProgress(models.Model):
    """Прогресс по уроку — отметка «пройден»."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lesson_progress",
        verbose_name=_("Пользователь"),
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="progress",
        verbose_name=_("Урок"),
    )
    completed_at = models.DateTimeField(_("Дата прохождения"), auto_now=True)

    class Meta:
        unique_together = ["user", "lesson"]
        verbose_name = _("Прогресс урока")
        verbose_name_plural = _("Прогресс уроков")


class LessonAiMessage(models.Model):
    """Сообщение диалога с ИИ по конкретному уроку."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lesson_ai_messages",
        verbose_name=_("Пользователь"),
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="ai_messages",
        verbose_name=_("Урок"),
    )
    question = models.TextField(_("Вопрос"))
    answer = models.TextField(_("Ответ"), blank=True)
    created_at = models.DateTimeField(_("Время"), auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Сообщение ИИ по уроку")
        verbose_name_plural = _("Сообщения ИИ по урокам")


class CourseReview(models.Model):
    """Отзыв о курсе от студента."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="course_reviews",
        verbose_name=_("Пользователь"),
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name=_("Курс"),
    )
    rating = models.PositiveSmallIntegerField(
        _("Оценка"),
        choices=[(i, str(i)) for i in range(1, 6)],
        default=5,
    )
    text = models.TextField(_("Текст отзыва"), blank=True)
    created_at = models.DateTimeField(_("Дата"), auto_now_add=True)

    class Meta:
        unique_together = ["user", "course"]
        ordering = ["-created_at"]
        verbose_name = _("Отзыв о курсе")
        verbose_name_plural = _("Отзывы о курсах")

    def __str__(self):
        return f"{self.user.username} — {self.course.title}: {self.rating}"
