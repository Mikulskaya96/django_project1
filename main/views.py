from django.shortcuts import render
from courses.models import Course


def index(request):
    """Главная страница DevLearn."""
    courses_preview = Course.objects.filter(is_active=True).select_related("category", "author").order_by("-created_at")[:4]
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
    return render(request, "main/about.html")
