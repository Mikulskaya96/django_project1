from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin
from .models import (
    Category,
    Course,
    Book,
    Lesson,
    Enrollment,
    LessonProgress,
    CourseReview,
)


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
    readonly_fields = ("created_at",)
    fields = (
        "title",
        "description",
        "level",
        "category",
        "author",
        "cover_image",
        "author_image",
        "price",
        "is_active",
        "created_at",
    )
    inlines = [LessonInline, BookInline]


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "enrolled_at")
    list_filter = ("course",)


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ("user", "lesson", "completed_at")


@admin.register(Lesson)
class LessonAdmin(MarkdownxModelAdmin):
    list_display = ("title", "course", "order")


@admin.register(CourseReview)
class CourseReviewAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "rating", "created_at")
    list_filter = ("course", "rating")
