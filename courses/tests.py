"""Smoke-тесты для списка курсов и публичного API."""

from django.conf import settings
from django.test import Client, TestCase


class CourseListViewTest(TestCase):
    """Страница списка курсов (i18n-префикс)."""

    def setUp(self):
        self.client = Client()

    def test_course_list_returns_200(self):
        response = self.client.get(f"/{settings.LANGUAGE_CODE}/courses/")
        self.assertEqual(response.status_code, 200)


class CoursesApiTest(TestCase):
    """Публичное REST API (AllowAny)."""

    def setUp(self):
        self.client = Client()

    def test_api_courses_list_returns_200(self):
        response = self.client.get("/api/courses/")
        self.assertEqual(response.status_code, 200)

    def test_api_root_returns_200(self):
        response = self.client.get("/api/")
        self.assertEqual(response.status_code, 200)
