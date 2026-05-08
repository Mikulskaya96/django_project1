"""Корневые маршруты (API, вебхук Stripe, i18n-префикс)."""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

from django.conf.urls.i18n import i18n_patterns
from courses.views import stripe_webhook

urlpatterns = [
    path("api/", include("courses.api_urls")),
    path("markdownx/", include("markdownx.urls")),
    path("i18n/", include("django.conf.urls.i18n")),
    # Webhook должен быть вне i18n_patterns, иначе Stripe получает redirect (302).
    path("courses/stripe/webhook/", stripe_webhook, name="stripe_webhook_public"),
    # Корень «/» → язык по умолчанию (LANGUAGE_CODE), т.е. /ru/
    path(
        "",
        RedirectView.as_view(
            url=f"/{settings.LANGUAGE_CODE}/",
            permanent=False,
        ),
    ),
]

urlpatterns += i18n_patterns(
    path("admin/", admin.site.urls),
    path("", include("main.urls")),
    path("users/", include("users.urls", namespace="users")),
    path("courses/", include("courses.urls", namespace="courses")),
    prefix_default_language=True,
)

# Раздача медиа (аватары) — и в dev, и на Render
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
