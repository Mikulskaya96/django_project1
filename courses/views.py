from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy

from .models import Category, Course, Book, Lesson, Enrollment, LessonProgress
from .forms import CourseCreateForm


class CourseListView(ListView):
    """Список курсов. Можно фильтровать по категории (?category=id)."""

    model = Course
    template_name = "courses/course_list.html"
    context_object_name = "courses"

    def get_queryset(self):
        qs = Course.objects.select_related("author", "category")
        cat = self.request.GET.get("category")
        if cat:
            qs = qs.filter(category_id=cat)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        return context


class CourseDetailView(DetailView):
    """Страница курса: название, описание, список уроков.
    Список уроков виден всем, содержимое — только записанным."""

    model = Course
    template_name = "courses/course_detail.html"
    context_object_name = "course"

    def get_queryset(self):
        return Course.objects.prefetch_related("lessons", "books").select_related("author", "category")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["is_enrolled"] = False
        if user.is_authenticated:
            context["is_enrolled"] = Enrollment.objects.filter(
                student=user, course=self.object
            ).exists()
        return context


class LessonDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Страница урока. Доступ только если записан на курс."""

    model = Lesson
    template_name = "courses/lesson_detail.html"
    context_object_name = "lesson"

    def get_queryset(self):
        return Lesson.objects.select_related("course")

    def test_func(self):
        lesson = self.get_object()
        return Enrollment.objects.filter(
            student=self.request.user, course=lesson.course
        ).exists()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lesson = self.object
        progress = LessonProgress.objects.filter(
            user=self.request.user, lesson=lesson
        ).first()
        context["is_completed"] = progress is not None
        return context


class MyCoursesView(LoginRequiredMixin, ListView):
    """Мои курсы + процент прохождения (пройдено/всего уроков)."""

    template_name = "courses/my_courses.html"
    context_object_name = "enrollments"

    def get_queryset(self):
        return (
            Enrollment.objects.filter(student=self.request.user)
            .select_related("course", "course__author")
            .prefetch_related("course__lessons")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.db.models import Count

        user = self.request.user
        course_ids = [e.course_id for e in context["enrollments"]]
        completed_counts = (
            LessonProgress.objects.filter(user=user, lesson__course_id__in=course_ids)
            .values("lesson__course_id")
            .annotate(cnt=Count("id"))
        )
        completed_by_course = {r["lesson__course_id"]: r["cnt"] for r in completed_counts}
        progress_list = []
        for e in context["enrollments"]:
            total = len(e.course.lessons.all())
            completed = completed_by_course.get(e.course_id, 0)
            progress_list.append({"enrollment": e, "total": total, "completed": completed})
        context["progress_list"] = progress_list
        return context


@login_required
def enroll_course(request, pk):
    """Записаться на курс. Создаёт запись Enrollment."""
    course = get_object_or_404(Course, pk=pk)
    Enrollment.objects.get_or_create(student=request.user, course=course)
    messages.success(request, f"Вы записаны на курс «{course.title}»")
    return redirect("courses:course_detail", pk=pk)


class CourseCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Создать курс. Только для роли «Преподаватель»."""

    model = Course
    form_class = CourseCreateForm
    template_name = "courses/course_form.html"
    success_url = reverse_lazy("courses:course_list")

    def test_func(self):
        profile = getattr(self.request.user, "profile", None)
        return profile and profile.role == "teacher"

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, "Курс создан")
        return super().form_valid(form)


@login_required
def complete_lesson(request, pk):
    """Отметить урок как пройденный."""
    lesson = get_object_or_404(Lesson, pk=pk)
    if Enrollment.objects.filter(student=request.user, course=lesson.course).exists():
        LessonProgress.objects.get_or_create(user=request.user, lesson=lesson)
        messages.success(request, "Урок отмечен как пройденный")
    return redirect("courses:lesson_detail", pk=pk)


def book_redirect(request, pk):
    """Переход по ссылке книги. Исправляет URL без https://."""
    book = get_object_or_404(Book, pk=pk)
    url = book.url.strip()
    if url and not url.startswith(("http://", "https://")):
        url = "https://" + url
    return redirect(url)
