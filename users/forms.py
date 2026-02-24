from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    """Форма регистрации. Расширяет стандартную UserCreationForm,
    добавляя email и выбор роли."""

    email = forms.EmailField(required=True)
    role = forms.ChoiceField(
        choices=[("student", "Студент"), ("teacher", "Преподаватель")],
        required=True,
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
