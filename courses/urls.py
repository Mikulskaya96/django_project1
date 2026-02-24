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
]
