from django.conf import settings
from django.db.models import Prefetch
from django.shortcuts import render
from courses.models import Course, Lesson


def index(request):
    """Главная страница DevLearn."""
    courses_preview = (
        Course.objects.filter(is_active=True)
        .select_related("category", "author")
        .prefetch_related(Prefetch("lessons", queryset=Lesson.objects.order_by("order", "id")))
        .order_by("-created_at")[:4]
    )
    return render(request, "main/index.html", {"courses_preview": courses_preview})


def public_offer(request):
    """Публичная оферта."""
    return render(request, "main/public_offer.html")


def privacy_policy(request):
    """Политика конфиденциальности."""
    return render(request, "main/privacy_policy.html")


def contacts(request):
    """Контакты и поддержка."""
    return render(request, "main/contacts.html")


def about(request):
    """О нас — миссия, команда, подход к обучению."""
    return render(
        request,
        "main/about.html",
        {
            "free_public_access": getattr(settings, "FREE_PUBLIC_ACCESS", True),
        },
    )
