from django import forms
from .models import Course
from django.contrib.auth.models import User


class EnrollStudentForm(forms.Form):
    """Форма для преподавателя: выбрать студента и записать на курс."""
    student = forms.ModelChoiceField(
        queryset=User.objects.none(),
        label="Студент",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Показываем только пользователей с ролью student (если есть профиль)
        self.fields["student"].queryset = User.objects.filter(profile__role="student").order_by("username")


class CourseCreateForm(forms.ModelForm):
    """Форма создания курса. Используется преподавателями."""

    class Meta:
        model = Course
        fields = ("title", "description", "category", "price")


class GradeForm(forms.Form):
    """Форма выставления оценки студенту по курсу. Только для преподавателей."""

    course = forms.ModelChoiceField(
        queryset=Course.objects.none(),
        label="Курс",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    grade = forms.TypedChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],
        coerce=int,
        label="Оценка",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
