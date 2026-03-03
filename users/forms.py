from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Profile


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
            "avatar": forms.FileInput(attrs={"accept": "image/*"}),
        }
