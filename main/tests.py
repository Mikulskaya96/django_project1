from django.test import TestCase, Client


class MainViewsTest(TestCase):
    """Проверка главной страницы."""

    def setUp(self):
        self.client = Client()

    def test_index_returns_200(self):
        # Корень «/» редиректит на /ru/ (или LANGUAGE_CODE) — см. settings.urls
        response = self.client.get("/", follow=True)
        self.assertEqual(response.status_code, 200)
