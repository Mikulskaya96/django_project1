from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    """Профиль пользователя — расширяет стандартного User.
    Позволяет хранить аватар, роль (Студент/Преподаватель) и доступ к платному контенту."""

    ROLE_CHOICES = [
        ("student", "Студент"),
        ("teacher", "Преподаватель"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        null=True,
        verbose_name="Аватар",
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default="student",
    )
    has_access = models.BooleanField(
        "Есть доступ к платному контенту",
        default=False,
    )

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"
