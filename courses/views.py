import os

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
from django.utils import timezone
from django.utils.translation import gettext as _, get_language

from .models import (
    Course,
    Book,
    Lesson,
    Enrollment,
    LessonProgress,
    LessonAiMessage,
    CourseReview,
)
from .forms import CourseCreateForm, EnrollStudentForm, CourseReviewForm
from .templatetags.course_extras import translate_content as translate_lesson_content


def free_lessons_count_for_course(course: Course) -> int:
    """Сколько первых уроков доступны без оплаты: junior — 2, pro — 1."""
    if course.level == Course.LEVEL_PRO:
        return 1
    return 2


def _effective_has_access(user) -> bool:
    """Полный доступ к платным урокам: оплата (has_access) или режим FREE_PUBLIC_ACCESS."""
    if not user.is_authenticated:
        return False
    if getattr(settings, "FREE_PUBLIC_ACCESS", False):
        return True
    profile = getattr(user, "profile", None)
    return bool(profile and getattr(profile, "has_access", False))

def _user_has_lesson_access(user, lesson: Lesson) -> bool:
    """Проверяет доступ пользователя к уроку с учётом бесплатных уроков и платного доступа."""
    if not user.is_authenticated:
        return False

    profile = getattr(user, "profile", None)
    is_teacher = bool(profile and getattr(profile, "role", "") == "teacher")

    if is_teacher or _effective_has_access(user):
        return True

    lessons = list(lesson.course.lessons.all().order_by("order", "id"))
    try:
        index = lessons.index(lesson) + 1
    except ValueError:
        index = free_lessons_count_for_course(lesson.course) + 1

    limit = free_lessons_count_for_course(lesson.course)
    is_free = index <= limit
    return is_free


class CourseListView(ListView):
    """Список курсов. Можно фильтровать по категории (?category=id)."""

    model = Course
    template_name = "courses/course_list.html"
    context_object_name = "courses"

    def get_queryset(self):
        from django.db.models import Count
        qs = Course.objects.filter(is_active=True).select_related("author", "category").annotate(
            lesson_count=Count("lessons")
        )
        cat = self.request.GET.get("category")
        if cat:
            qs = qs.filter(category_id=cat)
        level = self.request.GET.get("level")
        if level:
            qs = qs.filter(level=level)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["bundle_price_usd"] = getattr(settings, "BUNDLE_PRICE_USD", 4)
        context["free_public_access"] = getattr(settings, "FREE_PUBLIC_ACCESS", False)
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
        has_access = _effective_has_access(user) if user.is_authenticated else False
        is_teacher = bool(profile and getattr(profile, "role", "") == "teacher")

        is_enrolled = False
        completed_count = 0
        if user.is_authenticated:
            is_enrolled = Enrollment.objects.filter(
                student=user, course=course
            ).exists()
            if is_enrolled:
                lesson_ids = [l.pk for l in course.lessons.all()]
                completed_count = LessonProgress.objects.filter(
                    user=user, lesson_id__in=lesson_ids
                ).count()

        lessons = list(course.lessons.all().order_by("order", "id"))
        free_n = free_lessons_count_for_course(course)
        for idx, lesson in enumerate(lessons, start=1):
            is_free = idx <= free_n
            lesson.is_free = is_free
            lesson.is_locked = not (is_free or has_access or is_teacher)
            lesson.display_order = idx

        # Группировка по модулям для курса Junior
        lesson_modules = None
        if course.level == "junior" and len(lessons) >= 15:
            JUNIOR_MODULES = [
                ("Модуль 1", 0, 5),
                ("Модуль 2. Повторение и данные", 5, 10),
                ("Модуль 3. Функции и простой проект", 10, 15),
            ]
            lesson_modules = []
            for title, start, end in JUNIOR_MODULES:
                module_lessons = lessons[start:end]
                if module_lessons:
                    lesson_modules.append({"title": title, "lessons": module_lessons})

        context["is_enrolled"] = is_enrolled
        context["has_access"] = has_access
        context["is_teacher"] = is_teacher
        context["lessons"] = lessons
        context["lesson_modules"] = lesson_modules
        context["lesson_count"] = len(lessons)
        context["completed_count"] = completed_count
        context["bundle_price_usd"] = getattr(settings, "BUNDLE_PRICE_USD", 4)
        context["free_lessons_preview"] = free_n
        context["free_public_access"] = getattr(settings, "FREE_PUBLIC_ACCESS", False)

        reviews = CourseReview.objects.filter(course=course).select_related("user").order_by("-created_at")
        context["reviews"] = reviews

        user_review = None
        if user.is_authenticated:
            user_review = CourseReview.objects.filter(course=course, user=user).first()
        context["user_review"] = user_review
        context["review_form"] = CourseReviewForm(instance=user_review) if is_enrolled else None

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
            {
                "lesson": lesson,
                "course": lesson.course,
                "bundle_price_usd": getattr(settings, "BUNDLE_PRICE_USD", 4),
                "free_public_access": getattr(settings, "FREE_PUBLIC_ACCESS", False),
            },
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
        context["ai_messages"] = LessonAiMessage.objects.filter(
            user=self.request.user,
            lesson=lesson,
        )[:10]
        # Предыдущий и следующий урок
        lessons = list(lesson.course.lessons.all().order_by("order", "id"))
        idx = next((i for i, l in enumerate(lessons) if l.pk == lesson.pk), -1)
        context["prev_lesson"] = lessons[idx - 1] if idx > 0 else None
        context["next_lesson"] = lessons[idx + 1] if idx >= 0 and idx < len(lessons) - 1 else None
        context["lesson_list"] = lessons
        return context


@login_required
def ask_lesson_ai(request, pk):
    """Отвечает на вопрос по уроку через внешнюю AI-модель. POST: question."""
    if request.method != "POST":
        return JsonResponse({"error": _("Метод не разрешён")}, status=405)

    lesson = get_object_or_404(Lesson, pk=pk)
    user = request.user
    if not _user_has_lesson_access(user, lesson):
        return JsonResponse({"error": _("Нет доступа к этому уроку")}, status=403)

    question = (request.POST.get("question") or "").strip()
    if not question:
        return JsonResponse({"error": _("Введите вопрос")}, status=400)

    # Лимиты: без полного доступа — максимум 3 вопроса в день (см. _effective_has_access).
    if not _effective_has_access(user):
        now = timezone.now()
        start_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        used_today = LessonAiMessage.objects.filter(
            user=user,
            created_at__gte=start_day,
        ).count()
        if used_today >= 3:
            return JsonResponse(
                {
                    "error": _(
                        "Лимит бесплатных вопросов на сегодня исчерпан. Попробуйте завтра или оформите полный доступ."
                    )
                },
                status=429,
            )

    api_key = getattr(settings, "GROQ_API_KEY", "") or os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        return JsonResponse(
            {"error": _("AI не настроен. Добавьте GROQ_API_KEY в .env.")},
            status=503,
        )

    try:
        from groq import Groq

        client = Groq(api_key=api_key)
        # Те же переводы, что на странице урока (gettext), чтобы модель не вставляла русские названия в EN/IT
        lesson_title_for_ai = _(lesson.title)
        raw_body = lesson.content or ""
        context_ai = translate_lesson_content(raw_body)[:3000]
        ui_lang = get_language() or "ru"
        system_prompt = (
            "You are a helpful teaching assistant for a Python learning platform. "
            "Answer concisely and clearly; short code examples are welcome when useful.\n\n"
            "LANGUAGE RULE (critical): Write your entire reply in the same language the "
            "student's question is written in. Examples: if they ask in Italian, reply in Italian; "
            "if in English, in English; if in Russian, in Russian. "
            "If the question mixes languages, use the one that clearly dominates. "
            "The lesson topic line below is already in the student's UI language when translations exist; "
            "refer to it in that language. The lesson body may still be partly untranslated if truncated "
            "— still answer in the question's language and do not quote Russian headings in a non-Russian reply.\n\n"
            f"The student is viewing the site in locale «{ui_lang}» — use it only as a tie-breaker "
            "if the question language is ambiguous."
        )
        user_content = (
            f"Lesson topic: «{lesson_title_for_ai}».\n"
            f"Lesson context (may be empty; lines translated when possible, same as on the site):\n"
            f"{context_ai}\n\n"
            f"Student question (reply in THIS question's language):\n{question}"
        )
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
                {
                    "error": _(
                        "Модель вернула пустой ответ. Попробуйте переформулировать вопрос."
                    )
                },
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
        return JsonResponse({"error": _("Ошибка AI: %(err)s") % {"err": e}}, status=500)


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
            progress_list.append(
                {
                    "enrollment": e,
                    "total": total,
                    "completed": completed,
                }
            )
        context["progress_list"] = progress_list
        return context


@login_required
def enroll_course(request, pk):
    """Записаться на курс. Создаёт запись Enrollment."""
    course = get_object_or_404(Course, pk=pk)
    Enrollment.objects.get_or_create(student=request.user, course=course)
    messages.success(
        request,
        _("Вы записаны на курс «%(title)s»") % {"title": course.title},
    )
    return redirect("courses:course_detail", pk=pk)


@login_required
def add_review(request, pk):
    """Добавить или изменить отзыв о курсе. Только для записанных."""
    course = get_object_or_404(Course, pk=pk)
    if not Enrollment.objects.filter(student=request.user, course=course).exists():
        messages.error(request, _("Только записанные на курс могут оставлять отзывы."))
        return redirect("courses:course_detail", pk=pk)

    review = CourseReview.objects.filter(course=course, user=request.user).first()
    if request.method == "POST":
        form = CourseReviewForm(request.POST, instance=review)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.course = course
            obj.save()
            messages.success(request, _("Отзыв сохранён."))
            return redirect("courses:course_detail", pk=pk)
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
        messages.success(self.request, _("Курс создан"))
        return super().form_valid(form)


@login_required
def complete_lesson(request, pk):
    """Отметить урок как пройденный."""
    lesson = get_object_or_404(Lesson, pk=pk)
    if Enrollment.objects.filter(student=request.user, course=lesson.course).exists():
        LessonProgress.objects.get_or_create(user=request.user, lesson=lesson)
        messages.success(request, _("Урок отмечен как пройденный"))
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
        messages.error(
            request,
            _("Только преподаватель может записывать студентов на курс."),
        )
        return redirect("courses:course_detail", pk=pk)

    if request.method == "POST":
        form = EnrollStudentForm(request.POST)
        if form.is_valid():
            student = form.cleaned_data["student"]
            Enrollment.objects.get_or_create(student=student, course=course)
            messages.success(
                request,
                _("Студент %(username)s записан на курс «%(title)s»")
                % {"username": student.username, "title": course.title},
            )
            return redirect("courses:course_detail", pk=pk)
    else:
        form = EnrollStudentForm()

    return render(request, "courses/enroll_student.html", {"form": form, "course": course})


class StudentListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Список студентов. Только staff и superuser."""

    template_name = "courses/student_list.html"
    context_object_name = "students"
    paginate_by = 10
    login_url = reverse_lazy("users:login")

    def test_func(self):
        return self.request.user.is_superuser

    def get_queryset(self):
        return User.objects.filter(profile__role="student").select_related("profile")


class StudentDetailView(LoginRequiredMixin, DetailView):
    """Детальная информация о студенте. Staff/superuser видят всех, обычный пользователь — только себя."""

    model = User
    login_url = reverse_lazy("users:login")
    template_name = "courses/student_detail.html"
    context_object_name = "student"

    def get_queryset(self):
        return User.objects.filter(profile__role="student").select_related("profile")

    def dispatch(self, request, *args, **kwargs):
        """Обычный пользователь может видеть только свой профиль."""
        if not request.user.is_superuser:
            if int(kwargs.get("pk", 0)) != request.user.pk:
                from django.core.exceptions import PermissionDenied
                raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.object
        context["enrollments"] = Enrollment.objects.filter(student=student).select_related("course")
        return context


@login_required
def checkout(request):
    """Страница оплаты: показывает информацию и кнопку оплаты."""
    has_access = _effective_has_access(request.user)
    stripe_enabled = bool(
        settings.STRIPE_SECRET_KEY
        and settings.STRIPE_PRICE_ID
        and not getattr(settings, "FREE_PUBLIC_ACCESS", False)
    )
    return render(
        request,
        "courses/checkout.html",
        {
            "has_access": has_access,
            "price_usd": getattr(settings, "BUNDLE_PRICE_USD", 4),
            "stripe_enabled": stripe_enabled,
            "free_public_access": getattr(settings, "FREE_PUBLIC_ACCESS", False),
        },
    )


@login_required
def create_checkout_session(request):
    """Создаёт Stripe Checkout Session и перенаправляет пользователя на оплату."""
    if request.method != "POST":
        return redirect("courses:checkout")

    if not (settings.STRIPE_SECRET_KEY and settings.STRIPE_PRICE_ID):
        messages.error(request, _("Оплата ещё не настроена. Попробуйте позже."))
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
        messages.error(
            request,
            _("Ошибка при создании платежа: %(err)s") % {"err": e},
        )
        return redirect("courses:checkout")


@login_required
def checkout_success(request):
    """Страница после редиректа Stripe. Доступ выдаётся только через webhook."""
    session_id = request.GET.get("session_id")
    if not session_id:
        messages.info(
            request,
            _("Платёж обрабатывается. Обновите страницу через несколько секунд."),
        )
        return redirect("courses:course_list")

    if not settings.STRIPE_SECRET_KEY:
        messages.warning(
            request,
            _(
                "Платёж принят, но автоматическая проверка не настроена. Обратитесь в поддержку."
            ),
        )
        return redirect("courses:course_list")

    stripe.api_key = settings.STRIPE_SECRET_KEY
    try:
        session = stripe.checkout.Session.retrieve(session_id)
    except Exception:
        messages.info(
            request,
            _(
                "Платёж в обработке. Если доступ не откроется в течение минуты, обновите страницу."
            ),
        )
        return redirect("courses:course_list")

    if session.payment_status == "paid":
        messages.success(
            request,
            _("Оплата подтверждена. Доступ к курсам открыт."),
        )
    else:
        messages.info(
            request,
            _(
                "Платёж ещё не подтверждён. Доступ откроется автоматически после подтверждения Stripe."
            ),
        )
    return redirect("courses:course_list")


@login_required
def checkout_cancel(request):
    """Отмена оплаты: просто сообщение и возврат к курсам."""
    messages.info(request, _("Оплата была отменена."))
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
