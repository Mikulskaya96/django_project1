from django.conf import settings
from django.test import Client, TestCase


class MainViewsTest(TestCase):
    """Проверка главной страницы."""

    def setUp(self):
        self.client = Client()

    def test_index_returns_200(self):
        response = self.client.get(f"/{settings.LANGUAGE_CODE}/")
        self.assertEqual(response.status_code, 200)

    def test_root_redirects_to_default_language(self):
        response = self.client.get("/", follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn(f"/{settings.LANGUAGE_CODE}/", response.url)
