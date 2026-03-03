"""
Создаёт суперпользователя при деплое, если его ещё нет.
Для бесплатного Render (без Shell): задай в Environment переменные
DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, DJANGO_SUPERUSER_PASSWORD.
"""
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import Profile


class Command(BaseCommand):
    help = "Создаёт суперпользователя из переменных окружения, если ни одного нет (для деплоя без Shell)."

    def handle(self, *args, **options):
        User = get_user_model()
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write(self.style.SUCCESS("Суперпользователь уже есть, пропускаем."))
            return

        username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

        if not all([username, email, password]):
            self.stdout.write(
                self.style.WARNING(
                    "Переменные DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, "
                    "DJANGO_SUPERUSER_PASSWORD не заданы — суперпользователь не создан."
                )
            )
            return

        user = User.objects.create_superuser(username=username, email=email, password=password)
        Profile.objects.get_or_create(user=user, defaults={"role": "teacher"})
        self.stdout.write(self.style.SUCCESS(f"Суперпользователь «{username}» создан."))
