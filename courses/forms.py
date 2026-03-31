from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Course, CourseReview
from django.contrib.auth.models import User


class EnrollStudentForm(forms.Form):
    """Форма для преподавателя: выбрать студента и записать на курс."""
    student = forms.ModelChoiceField(
        queryset=User.objects.none(),
        label=_("Студент"),
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


class CourseReviewForm(forms.ModelForm):
    """Форма отзыва о курсе."""

    class Meta:
        model = CourseReview
        fields = ("rating", "text")
        labels = {"rating": _("Rating"), "text": _("Review text")}
        widgets = {
            "rating": forms.Select(attrs={"class": "form-styled"}),
            "text": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": _("Leave an optional review about the course..."),
                }
            ),
        }


