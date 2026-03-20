from django.shortcuts import render


def index(request):
    """Главная страница DevLearn."""
    return render(request, "main/index.html")


def public_offer(request):
    """Публичная оферта."""
    return render(request, "main/public_offer.html")


def privacy_policy(request):
    """Политика конфиденциальности."""
    return render(request, "main/privacy_policy.html")


def contacts(request):
    """Контакты и поддержка."""
    return render(request, "main/contacts.html")
