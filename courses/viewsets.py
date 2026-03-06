from rest_framework import viewsets, permissions
from .models import Category, Course, Lesson, Book, Enrollment
from .serializers import (
    CategorySerializer,
    CourseSerializer,
    CourseDetailSerializer,
    LessonSerializer,
    BookSerializer,
    EnrollmentSerializer,
)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """API для категорий курсов.
    GET /api/categories/ — список категорий
    GET /api/categories/{id}/ — детали категории
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    """API для курсов.
    GET /api/courses/ — список курсов
    GET /api/courses/{id}/ — детали курса с уроками и книгами
    """
    queryset = Course.objects.all()
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        """Используем разные сериализаторы для списка и детального просмотра."""
        if self.action == "retrieve":
            return CourseDetailSerializer
        return CourseSerializer


class LessonViewSet(viewsets.ReadOnlyModelViewSet):
    """API для уроков.
    GET /api/lessons/ — список всех уроков
    GET /api/lessons/{id}/ — детали урока
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.AllowAny]


class BookViewSet(viewsets.ReadOnlyModelViewSet):
    """API для рекомендуемых книг.
    GET /api/books/ — список книг
    GET /api/books/{id}/ — детали книги
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]


class EnrollmentViewSet(viewsets.ModelViewSet):
    """API для записи на курсы.
    GET /api/enrollments/ — список всех записей
    POST /api/enrollments/ — создать новую запись (записаться на курс)
    GET /api/enrollments/{id}/ — детали записи
    """
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.AllowAny]  # В продакшене нужна аутентификация
