"""Дополнительный контекст шаблонов."""

from django.conf import settings


def ga4(request):
    """ID Google Analytics 4 (G-…) для base.html; пустая строка — счётчик отключён."""
    return {
        "ga4_measurement_id": (getattr(settings, "GA4_MEASUREMENT_ID", "") or "").strip(),
    }
