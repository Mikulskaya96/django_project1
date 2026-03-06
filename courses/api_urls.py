from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import (
    CategoryViewSet,
    CourseViewSet,
    LessonViewSet,
    BookViewSet,
    EnrollmentViewSet,
)

# Создаем router и регистрируем ViewSets
router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="api-category")
router.register(r"courses", CourseViewSet, basename="api-course")
router.register(r"lessons", LessonViewSet, basename="api-lesson")
router.register(r"books", BookViewSet, basename="api-book")
router.register(r"enrollments", EnrollmentViewSet, basename="api-enrollment")

urlpatterns = [
    path("", include(router.urls)),
]
