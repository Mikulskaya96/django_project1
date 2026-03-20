import os
from io import BytesIO

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import stripe
from users.models import Profile
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import simpleSplit
from django.utils import timezone

from .models import (
    Category,
    Course,
    Book,
    Lesson,
    Enrollment,
    LessonProgress,
    Grade,
    LessonAiMessage,
    CourseCertificate,
)
from .forms import CourseCreateForm, EnrollStudentForm, GradeForm


FREE_LESSONS_PER_COURSE = 3


def _user_has_lesson_access(user, lesson: Lesson) -> bool:
    """Проверяет доступ пользователя к уроку с учётом бесплатных уроков и платного доступа."""
    if not user.is_authenticated:
        return False

    profile = getattr(user, "profile", None)
    has_access = bool(profile and getattr(profile, "has_access", False))
    is_teacher = bool(profile and getattr(profile, "role", "") == "teacher")

    if is_teacher or has_access:
        return True

    lessons = list(lesson.course.lessons.all().order_by("order", "id"))
    try:
        index = lessons.index(lesson) + 1
    except ValueError:
        index = FREE_LESSONS_PER_COURSE + 1

    is_free = index <= FREE_LESSONS_PER_COURSE
    return is_free


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
        level = self.request.GET.get("level")
        if level:
            qs = qs.filter(level=level)
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
        course = self.object

        profile = getattr(user, "profile", None) if user.is_authenticated else None
        has_access = bool(profile and getattr(profile, "has_access", False))
        is_teacher = bool(profile and getattr(profile, "role", "") == "teacher")

        is_enrolled = False
        if user.is_authenticated:
            is_enrolled = Enrollment.objects.filter(
                student=user, course=course
            ).exists()

        lessons = list(course.lessons.all().order_by("order", "id"))
        for idx, lesson in enumerate(lessons, start=1):
            is_free = idx <= FREE_LESSONS_PER_COURSE
            lesson.is_free = is_free
            lesson.is_locked = not (is_free or has_access or is_teacher)

        context["is_enrolled"] = is_enrolled
        context["has_access"] = has_access
        context["is_teacher"] = is_teacher
        context["lessons"] = lessons
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
        return _user_has_lesson_access(self.request.user, lesson)

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        lesson = self.get_object()
        return render(
            self.request,
            "courses/access_denied.html",
            {"lesson": lesson, "course": lesson.course},
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lesson = self.object
        progress = LessonProgress.objects.filter(
            user=self.request.user, lesson=lesson
        ).first()
        context["is_completed"] = progress is not None
        context["gemini_available"] = bool(
            getattr(settings, "GROQ_API_KEY", "") or os.environ.get("GROQ_API_KEY", "")
        )
        # История последних вопросов к ИИ по уроку
        context["ai_messages"] = LessonAiMessage.objects.filter(
            user=self.request.user,
            lesson=lesson,
        )[:10]
        return context


@login_required
def ask_lesson_ai(request, pk):
    """Отвечает на вопрос по уроку через внешнюю AI-модель. POST: question."""
    if request.method != "POST":
        return JsonResponse({"error": "Метод не разрешён"}, status=405)

    lesson = get_object_or_404(Lesson, pk=pk)
    user = request.user
    if not _user_has_lesson_access(user, lesson):
        return JsonResponse({"error": "Нет доступа к этому уроку"}, status=403)

    question = (request.POST.get("question") or "").strip()
    if not question:
        return JsonResponse({"error": "Введите вопрос"}, status=400)

    # Лимиты: бесплатным пользователям, без has_access — максимум 3 вопроса в день.
    profile = getattr(user, "profile", None)
    has_access = bool(profile and getattr(profile, "has_access", False))
    if not has_access:
        from django.utils import timezone

        now = timezone.now()
        start_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        used_today = LessonAiMessage.objects.filter(
            user=user,
            created_at__gte=start_day,
        ).count()
        if used_today >= 3:
            return JsonResponse(
                {"error": "Лимит бесплатных вопросов на сегодня исчерпан. Попробуйте завтра или оформите полный доступ."},
                status=429,
            )

    api_key = getattr(settings, "GROQ_API_KEY", "") or os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        return JsonResponse({"error": "AI не настроен. Добавьте GROQ_API_KEY в .env."}, status=503)

    try:
        from groq import Groq

        client = Groq(api_key=api_key)
        context = (lesson.content or "")[:3000]
        system_prompt = (
            "Ты — доброжелательный ассистент на учебной платформе по Python. "
            "Отвечай кратко, по делу и на понятном русском языке, можно с небольшими примерами кода."
        )
        user_content = f"""Тема урока: «{lesson.title}».
Контекст урока (может быть пустым):
{context}

Вопрос студента: {question}
"""
        resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            temperature=0.2,
            max_tokens=512,
        )
        answer = (resp.choices[0].message.content or "").strip()
        if not answer:
            return JsonResponse(
                {"error": "Модель вернула пустой ответ. Попробуйте переформулировать вопрос."},
                status=502,
            )
        LessonAiMessage.objects.create(
            user=user,
            lesson=lesson,
            question=question,
            answer=answer,
        )
        return JsonResponse({"answer": answer})
    except Exception as e:
        return JsonResponse({"error": f"Ошибка AI: {e}"}, status=500)


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
            is_completed = total > 0 and completed >= total
            certificate = None
            if is_completed:
                certificate = CourseCertificate.objects.filter(
                    user=user,
                    course=e.course,
                ).first()
            progress_list.append(
                {
                    "enrollment": e,
                    "total": total,
                    "completed": completed,
                    "is_completed": is_completed,
                    "certificate": certificate,
                }
            )
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
        # Форма оценки — только для преподавателей; курсы только те, на которые записан студент
        profile = getattr(self.request.user, "profile", None)
        if profile and profile.role == "teacher":
            context["grade_form"] = GradeForm()
            context["grade_form"].fields["course"].queryset = Course.objects.filter(
                enrollments__student=student
            ).distinct()
        else:
            context["grade_form"] = None
        return context


@login_required
def add_grade(request, pk):
    """Поставить или изменить оценку студенту по курсу. Только преподаватели."""
    student = get_object_or_404(User, pk=pk, profile__role="student")
    profile = getattr(request.user, "profile", None)
    if not (profile and profile.role == "teacher"):
        messages.error(request, "Только преподаватель может выставлять оценки.")
        return redirect("courses:student_detail", pk=pk)

    if request.method != "POST":
        return redirect("courses:student_detail", pk=pk)

    courses_qs = Course.objects.filter(enrollments__student=student).distinct()
    form = GradeForm(request.POST)
    form.fields["course"].queryset = courses_qs

    if request.method == "POST" and form.is_valid():
        course = form.cleaned_data["course"]
        grade_value = form.cleaned_data["grade"]
        Grade.objects.update_or_create(
            student=student,
            course=course,
            defaults={"grade": grade_value},
        )
        messages.success(request, f"Оценка {grade_value} по курсу «{course.title}» сохранена.")
        return redirect("courses:student_detail", pk=pk)

    # GET или невалидная форма — показываем страницу студента с формой
    enrollments = Enrollment.objects.filter(student=student).select_related("course")
    grades = Grade.objects.filter(student=student).select_related("course")
    return render(
        request,
        "courses/student_detail.html",
        {
            "student": student,
            "enrollments": enrollments,
            "grades": grades,
            "grade_form": form,
        },
    )


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


@login_required
def checkout(request):
    """Страница оплаты: показывает информацию и кнопку оплаты."""
    profile = getattr(request.user, "profile", None)
    has_access = bool(profile and getattr(profile, "has_access", False))
    stripe_enabled = bool(settings.STRIPE_SECRET_KEY and settings.STRIPE_PRICE_ID)
    return render(
        request,
        "courses/checkout.html",
        {
            "has_access": has_access,
            "price_usd": 4,
            "stripe_enabled": stripe_enabled,
        },
    )


@login_required
def create_checkout_session(request):
    """Создаёт Stripe Checkout Session и перенаправляет пользователя на оплату."""
    if request.method != "POST":
        return redirect("courses:checkout")

    if not (settings.STRIPE_SECRET_KEY and settings.STRIPE_PRICE_ID):
        messages.error(request, "Оплата ещё не настроена. Попробуйте позже.")
        return redirect("courses:checkout")

    stripe.api_key = settings.STRIPE_SECRET_KEY

    success_url = request.build_absolute_uri(
        reverse_lazy("courses:checkout_success")
    ) + "?session_id={CHECKOUT_SESSION_ID}"
    cancel_url = request.build_absolute_uri(reverse_lazy("courses:checkout_cancel"))

    try:
        session = stripe.checkout.Session.create(
            mode="payment",
            line_items=[{"price": settings.STRIPE_PRICE_ID, "quantity": 1}],
            success_url=success_url,
            cancel_url=cancel_url,
            customer_email=request.user.email or None,
            metadata={"user_id": request.user.id},
        )
        return redirect(session.url)
    except Exception as e:
        messages.error(request, f"Ошибка при создании платежа: {e}")
        return redirect("courses:checkout")


@login_required
def checkout_success(request):
    """Страница после редиректа Stripe. Доступ выдаётся только через webhook."""
    session_id = request.GET.get("session_id")
    if not session_id:
        messages.info(
            request,
            "Платёж обрабатывается. Обновите страницу через несколько секунд.",
        )
        return redirect("courses:course_list")

    if not settings.STRIPE_SECRET_KEY:
        messages.warning(
            request,
            "Платёж принят, но автоматическая проверка не настроена. Обратитесь в поддержку.",
        )
        return redirect("courses:course_list")

    stripe.api_key = settings.STRIPE_SECRET_KEY
    try:
        session = stripe.checkout.Session.retrieve(session_id)
    except Exception:
        messages.info(
            request,
            "Платёж в обработке. Если доступ не откроется в течение минуты, обновите страницу.",
        )
        return redirect("courses:course_list")

    if session.payment_status == "paid":
        messages.success(request, "Оплата подтверждена. Доступ к курсам открыт.")
    else:
        messages.info(
            request,
            "Платёж ещё не подтверждён. Доступ откроется автоматически после подтверждения Stripe.",
        )
    return redirect("courses:course_list")


@login_required
def checkout_cancel(request):
    """Отмена оплаты: просто сообщение и возврат к курсам."""
    messages.info(request, "Оплата была отменена.")
    return redirect("courses:checkout")


@csrf_exempt
def stripe_webhook(request):
    """Webhook Stripe: подтверждает оплату и выдаёт доступ пользователю."""
    if request.method != "POST":
        return HttpResponse(status=405)

    webhook_secret = getattr(settings, "STRIPE_WEBHOOK_SECRET", "")
    if not webhook_secret:
        return HttpResponse(status=503)

    payload = request.body
    signature = request.META.get("HTTP_STRIPE_SIGNATURE", "")

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=signature,
            secret=webhook_secret,
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        if session.get("payment_status") == "paid":
            user_id = (session.get("metadata") or {}).get("user_id")
            if user_id:
                try:
                    profile = Profile.objects.get(user_id=int(user_id))
                    if not profile.has_access:
                        profile.has_access = True
                        profile.save(update_fields=["has_access"])
                except (Profile.DoesNotExist, ValueError, TypeError):
                    pass

    return HttpResponse(status=200)


@login_required
def download_certificate(request, course_id):
    """Генерирует и отдаёт PDF-сертификат, если курс завершён."""
    course = get_object_or_404(Course, pk=course_id)
    user = request.user

    if not Enrollment.objects.filter(student=user, course=course).exists():
        messages.error(request, "Вы не записаны на этот курс.")
        return redirect("courses:my_courses")

    total_lessons = Lesson.objects.filter(course=course).count()
    completed_lessons = LessonProgress.objects.filter(
        user=user,
        lesson__course=course,
    ).count()

    if total_lessons == 0 or completed_lessons < total_lessons:
        messages.info(request, "Сертификат доступен после завершения всех уроков курса.")
        return redirect("courses:my_courses")

    certificate, _ = CourseCertificate.objects.get_or_create(user=user, course=course)

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    pdf.setTitle(f"Certificate-{certificate.certificate_id}")

    y = height - 90
    pdf.setFont("Helvetica-Bold", 26)
    pdf.drawCentredString(width / 2, y, "DevLearn Certificate")

    y -= 50
    pdf.setFont("Helvetica", 13)
    pdf.drawCentredString(width / 2, y, "This certifies that")

    y -= 35
    full_name = user.get_full_name().strip() or user.username
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawCentredString(width / 2, y, full_name)

    y -= 40
    pdf.setFont("Helvetica", 13)
    pdf.drawCentredString(width / 2, y, "has successfully completed the course")

    y -= 30
    pdf.setFont("Helvetica-Bold", 16)
    for line in simpleSplit(course.title, "Helvetica-Bold", 16, width - 120):
        pdf.drawCentredString(width / 2, y, line)
        y -= 22

    y -= 10
    issued_date = timezone.localtime(certificate.issued_at).strftime("%Y-%m-%d")
    pdf.setFont("Helvetica", 12)
    pdf.drawCentredString(width / 2, y, f"Issued: {issued_date}")
    y -= 20
    pdf.drawCentredString(width / 2, y, f"Certificate ID: {certificate.certificate_id}")

    y -= 70
    pdf.line(90, y, 250, y)
    pdf.line(width - 250, y, width - 90, y)
    pdf.setFont("Helvetica", 10)
    pdf.drawString(125, y - 14, "Instructor")
    pdf.drawRightString(width - 125, y - 14, "DevLearn")

    pdf.showPage()
    pdf.save()
    buffer.seek(0)

    filename = f"certificate-{course_id}-{user.username}.pdf"
    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response
