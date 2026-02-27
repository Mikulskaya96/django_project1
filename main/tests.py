from django.test import TestCase, Client


class MainViewsTest(TestCase):
    """Проверка главной страницы."""

    def setUp(self):
        self.client = Client()

    def test_index_returns_200(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
