from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class Profile(models.Model):
    """Профиль пользователя — расширяет стандартного User.
    Позволяет хранить аватар, роль (Студент/Преподаватель) и доступ к платному контенту."""

    ROLE_CHOICES = [
        ("student", _("Студент")),
        ("teacher", _("Преподаватель")),
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
        verbose_name=_("Аватар"),
    )
    role = models.CharField(
        _("Роль"),
        max_length=10,
        choices=ROLE_CHOICES,
        default="student",
    )
    has_access = models.BooleanField(
        _("Есть доступ к платному контенту"),
        default=False,
    )

    class Meta:
        verbose_name = _("Профиль")
        verbose_name_plural = _("Профили")

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"
