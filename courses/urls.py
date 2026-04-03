from django.urls import path

from . import views

app_name = "courses"

urlpatterns = [
    path("", views.CourseListView.as_view(), name="course_list"),
    path("create/", views.CourseCreateView.as_view(), name="course_create"),
    path("my/", views.MyCoursesView.as_view(), name="my_courses"),
    path("checkout/", views.checkout, name="checkout"),
    path("checkout/session/", views.create_checkout_session, name="create_checkout_session"),
    path("checkout/success/", views.checkout_success, name="checkout_success"),
    path("checkout/cancel/", views.checkout_cancel, name="checkout_cancel"),
    path("<int:pk>/", views.CourseDetailView.as_view(), name="course_detail"),
    path("<int:pk>/enroll/", views.enroll_course, name="enroll"),
    path("<int:pk>/review/", views.add_review, name="add_review"),
    path("lesson/<int:pk>/", views.LessonDetailView.as_view(), name="lesson_detail"),
    path("lesson/<int:pk>/complete/", views.complete_lesson, name="complete_lesson"),
    path("lesson/<int:pk>/ask-ai/", views.ask_lesson_ai, name="ask_lesson_ai"),
    path("book/<int:pk>/go/", views.book_redirect, name="book_redirect"),
    # Студенты
    path("students/", views.StudentListView.as_view(), name="student_list"),
    path("students/<int:pk>/", views.StudentDetailView.as_view(), name="student_detail"),
    # Запись студентов (только для преподавателей)
    path("<int:pk>/enroll-student/", views.enroll_student, name="enroll_student"),
]
