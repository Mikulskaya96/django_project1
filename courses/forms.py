from django import forms
from .models import Course


class CourseCreateForm(forms.ModelForm):
    """Форма создания курса. Используется преподавателями."""

    class Meta:
        model = Course
        fields = ("title", "description", "category", "price")
