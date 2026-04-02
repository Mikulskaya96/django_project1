from django.conf import settings
from django.test import TestCase, Client


class MainViewsTest(TestCase):
    """Проверка главной страницы."""

    def setUp(self):
        self.client = Client()

    def test_index_returns_200(self):
        # Главная под i18n: /ru/, /en/ и т.д. — надёжнее, чем follow по / (цепочки редиректов в CI)
        response = self.client.get(f"/{settings.LANGUAGE_CODE}/")
        self.assertEqual(response.status_code, 200)

    def test_root_redirects_to_default_language(self):
        response = self.client.get("/", follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn(f"/{settings.LANGUAGE_CODE}/", response["Location"])
