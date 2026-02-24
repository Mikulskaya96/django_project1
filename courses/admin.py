from django.contrib import admin
from .models import Category, Course, Book, Lesson, Enrollment, LessonProgress


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0


class BookInline(admin.TabularInline):
    model = Book
    extra = 0


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "author", "price", "created_at")
    inlines = [LessonInline, BookInline]


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "enrolled_at")
    list_filter = ("course",)


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ("user", "lesson", "completed_at")
