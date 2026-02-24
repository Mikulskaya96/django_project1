from django.shortcuts import render


def index(request):
    """Главная страница DevLearn."""
    return render(request, "main/index.html")
