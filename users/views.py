import logging

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext as _

from .forms import RegisterForm, ProfileEditForm
from .models import Profile

logger = logging.getLogger(__name__)


@login_required
def profile_edit(request):
    """Редактирование своего профиля: загрузка аватара."""
    profile, _created = Profile.objects.get_or_create(
        user=request.user, defaults={"role": "student"}
    )
    if request.method == "POST":
        try:
            form = ProfileEditForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                try:
                    form.save()
                except Exception:
                    logger.exception("Profile avatar save failed")
                    messages.error(
                        request,
                        _(
                            "Не удалось сохранить файл. Проверьте CLOUDINARY_URL на сервере и размер изображения."
                        ),
                    )
                else:
                    messages.success(request, str(_("Профиль обновлён.")))
                    profile.refresh_from_db()
                    # 303 + тот же path: надёжный PRG при i18n-префиксе; 302 иногда даёт повторный POST.
                    response = HttpResponseRedirect(request.path)
                    response.status_code = 303
                    return response
        except Exception:
            logger.exception("Profile edit POST failed")
            messages.error(
                request,
                _(
                    "Не удалось обработать загрузку. Попробуйте изображение JPEG или PNG размером до 5 МБ."
                ),
            )
            form = ProfileEditForm(instance=profile)
    else:
        form = ProfileEditForm(instance=profile)
    return render(
        request,
        "users/profile_edit.html",
        {
            "form": form,
            "profile": profile,
            "free_public_access": getattr(settings, "FREE_PUBLIC_ACCESS", True),
        },
    )


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
