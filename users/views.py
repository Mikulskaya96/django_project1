from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.views.generic import CreateView
from django.urls import reverse_lazy

from .forms import RegisterForm
from .models import Profile


class RegisterView(CreateView):
    """Страница регистрации. Создаёт User и Profile с ролью."""

    form_class = RegisterForm
    template_name = "users/register.html"
    success_url = reverse_lazy("index")

    def form_valid(self, form):
        user = form.save(commit=False)
        user.email = form.cleaned_data["email"]
        user.save()
        Profile.objects.create(user=user, role="student")
        login(self.request, user, backend="django.contrib.auth.backends.ModelBackend")
        return redirect(self.success_url)
