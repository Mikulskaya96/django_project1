from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.conf import settings
from django.http import JsonResponse

from .models import Category, Course, Book, Lesson, Enrollment, LessonProgress, Grade
from .forms import CourseCreateForm, EnrollStudentForm


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
        context["gemini_available"] = bool(getattr(settings, "GEMINI_API_KEY", ""))
        return context


@login_required
def ask_lesson_ai(request, pk):
    """Отвечает на вопрос по уроку через Gemini. POST: question. Доступ только записанным на курс."""
    if request.method != "POST":
        return JsonResponse({"error": "Метод не разрешён"}, status=405)

    lesson = get_object_or_404(Lesson, pk=pk)
    if not Enrollment.objects.filter(student=request.user, course=lesson.course).exists():
        return JsonResponse({"error": "Нет доступа к этому курсу"}, status=403)

    question = (request.POST.get("question") or "").strip()
    if not question:
        return JsonResponse({"error": "Введите вопрос"}, status=400)

    api_key = getattr(settings, "GEMINI_API_KEY", "") or ""
    if not api_key:
        return JsonResponse({"error": "AI не настроен. Добавьте GEMINI_API_KEY в .env."}, status=503)

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        context = (lesson.content or "")[:3000]
        prompt = f"""Ты — помощник на учебной платформе. Тема урока: «{lesson.title}».
Контекст урока (может быть пустым):
{context}

Вопрос студента: {question}

Ответь кратко и по делу на русском."""
        # Пробуем модели по очереди (только ID, поддерживаемые Google AI Studio)
        last_error = None
        for model_name in ("gemini-2.0-flash", "gemini-pro"):
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                answer = (response.text or "").strip()
                if answer:
                    return JsonResponse({"answer": answer})
            except Exception as inner:
                last_error = inner
                s = str(inner)
                if "429" in s or "quota" in s.lower():
                    continue
                if "404" in s or "not found" in s.lower():
                    continue
                raise
        err_msg = "Превышен лимит запросов. Подождите минуту и попробуйте снова."
        if last_error and ("404" in str(last_error) or "not found" in str(last_error).lower()):
            err_msg = "Сейчас модель недоступна. Попробуйте позже."
        return JsonResponse({"error": err_msg}, status=503)
    except Exception as e:
        err = str(e)
        if "429" in err or "quota" in err.lower():
            return JsonResponse({
                "error": "Превышен лимит бесплатного API. Подождите минуту и попробуйте снова."
            }, status=429)
        return JsonResponse({"error": f"Ошибка: {err}"}, status=500)


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


@login_required
def enroll_student(request, pk):
    """Позволяет преподавателю записывать выбранного студента на курс."""
    course = get_object_or_404(Course, pk=pk)
    profile = getattr(request.user, "profile", None)
    if not (profile and profile.role == "teacher"):
        messages.error(request, "Только преподаватель может записывать студентов на курс.")
        return redirect("courses:course_detail", pk=pk)

    if request.method == "POST":
        form = EnrollStudentForm(request.POST)
        if form.is_valid():
            student = form.cleaned_data["student"]
            Enrollment.objects.get_or_create(student=student, course=course)
            messages.success(request, f"Студент {student.username} записан на курс «{course.title}»")
            return redirect("courses:course_detail", pk=pk)
    else:
        form = EnrollStudentForm()

    return render(request, "courses/enroll_student.html", {"form": form, "course": course})


class StudentListView(LoginRequiredMixin, ListView):
    """Список студентов. Доступ только авторизованным."""

    template_name = "courses/student_list.html"
    context_object_name = "students"
    paginate_by = 10
    login_url = reverse_lazy("users:login")

    def get_queryset(self):
        return User.objects.filter(profile__role="student").select_related("profile")


class StudentDetailView(LoginRequiredMixin, DetailView):
    """Детальная информация о студенте. Доступ только авторизованным."""

    model = User
    login_url = reverse_lazy("users:login")
    template_name = "courses/student_detail.html"
    context_object_name = "student"

    def get_queryset(self):
        return User.objects.filter(profile__role="student").select_related("profile")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.object
        # Курсы на которых записан студент
        context["enrollments"] = Enrollment.objects.filter(student=student).select_related("course")
        # Оценки студента
        context["grades"] = Grade.objects.filter(student=student).select_related("course")
        return context


class GradeBookView(LoginRequiredMixin, ListView):
    """Журнал оценок. Доступ только авторизованным."""

    template_name = "courses/grade_book.html"
    context_object_name = "grades"
    login_url = reverse_lazy("users:login")

    def get_queryset(self):
        return Grade.objects.select_related("student", "course").order_by("-date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем уникальные курсы для фильтра
        context["courses"] = Course.objects.all()
        # Фильтруем по курсу, если задан параметр (только валидный id)
        course_id = self.request.GET.get("course")
        if course_id and course_id.isdigit():
            context["grades"] = context["grades"].filter(course_id=int(course_id))
            context["selected_course"] = int(course_id)
        return context
