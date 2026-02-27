from django.urls import path

from . import views

app_name = "courses"

urlpatterns = [
    path("", views.CourseListView.as_view(), name="course_list"),
    path("create/", views.CourseCreateView.as_view(), name="course_create"),
    path("my/", views.MyCoursesView.as_view(), name="my_courses"),
    path("<int:pk>/", views.CourseDetailView.as_view(), name="course_detail"),
    path("<int:pk>/enroll/", views.enroll_course, name="enroll"),
    path("lesson/<int:pk>/", views.LessonDetailView.as_view(), name="lesson_detail"),
    path("lesson/<int:pk>/complete/", views.complete_lesson, name="complete_lesson"),
    path("book/<int:pk>/go/", views.book_redirect, name="book_redirect"),
    # Студенты и оценки
    path("students/", views.StudentListView.as_view(), name="student_list"),
    path("students/<int:pk>/", views.StudentDetailView.as_view(), name="student_detail"),
    path("grade-book/", views.GradeBookView.as_view(), name="grade_book"),
    # Запись студентов (только для преподавателей)
    path("<int:pk>/enroll-student/", views.enroll_student, name="enroll_student"),
]
