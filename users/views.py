from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib import messages

from .forms import RegisterForm, ProfileEditForm
from .models import Profile


@login_required
def profile_edit(request):
    """Редактирование своего профиля: загрузка аватара."""
    profile, _ = Profile.objects.get_or_create(user=request.user, defaults={"role": "student"})
    if request.method == "POST":
        form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Профиль обновлён.")
            return redirect("users:profile_edit")
    else:
        form = ProfileEditForm(instance=profile)
    return render(request, "users/profile_edit.html", {"form": form, "profile": profile})


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
