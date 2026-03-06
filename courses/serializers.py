from rest_framework import serializers
from .models import Category, Course, Lesson, Book, Enrollment


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий."""
    class Meta:
        model = Category
        fields = ["id", "name"]


class LessonSerializer(serializers.ModelSerializer):
    """Сериализатор для уроков."""
    class Meta:
        model = Lesson
        fields = ["id", "title", "content", "video_url", "order"]


class BookSerializer(serializers.ModelSerializer):
    """Сериализатор для книг."""
    class Meta:
        model = Book
        fields = ["id", "title", "url", "order"]


class CourseSerializer(serializers.ModelSerializer):
    """Сериализатор для курсов (список)."""
    category = CategorySerializer(read_only=True)
    author = serializers.StringRelatedField()
    
    class Meta:
        model = Course
        fields = ["id", "title", "description", "category", "author", "price", "created_at"]


class CourseDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для детальной информации о курсе."""
    category = CategorySerializer(read_only=True)
    author = serializers.StringRelatedField()
    lessons = LessonSerializer(many=True, read_only=True)
    books = BookSerializer(many=True, read_only=True)
    
    class Meta:
        model = Course
        fields = ["id", "title", "description", "category", "author", "price", "created_at", "lessons", "books"]


class EnrollmentSerializer(serializers.ModelSerializer):
    """Сериализатор для записи на курс."""
    student = serializers.StringRelatedField()
    course = serializers.StringRelatedField()
    
    class Meta:
        model = Enrollment
        fields = ["id", "student", "course", "enrolled_at"]
