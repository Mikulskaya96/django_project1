from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from PIL import Image

from .models import Profile

_AVATAR_MAX_BYTES = 5 * 1024 * 1024


class RegisterForm(UserCreationForm):
    """Форма регистрации. Расширяет стандартную UserCreationForm, добавляя email.
    Роль при регистрации всегда «студент»; преподавателя назначают в админке."""

    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class ProfileEditForm(forms.ModelForm):
    """Редактирование профиля: аватар, имя, фамилия."""

    class Meta:
        model = Profile
        fields = ("avatar",)
        widgets = {
            "avatar": forms.FileInput(
                attrs={
                    "accept": "image/*",
                    "class": "profile-upload__input",
                }
            ),
        }

    def clean_avatar(self):
        f = self.cleaned_data.get("avatar")
        if not f:
            return f
        if getattr(f, "size", 0) > _AVATAR_MAX_BYTES:
            raise ValidationError(_("Файл больше 5 МБ."))
        try:
            img = Image.open(f)
            img.load()
        except Exception:
            raise ValidationError(
                _("Не удалось прочитать изображение. Используйте JPEG или PNG.")
            )
        if hasattr(f, "seek"):
            f.seek(0)
        return f
