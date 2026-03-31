from django.urls import path
from .views import index, public_offer, privacy_policy, contacts, about

urlpatterns = [
    path("", index, name="index"),
    path("about/", about, name="about"),
    path("offer/", public_offer, name="public_offer"),
    path("privacy/", privacy_policy, name="privacy_policy"),
    path("contacts/", contacts, name="contacts"),
]
