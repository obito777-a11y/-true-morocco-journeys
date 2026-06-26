"""
api/urls.py — URL patterns for the True Morocco Journeys API.
"""
from django.urls import path
from . import views

urlpatterns = [
    path("health/", views.health, name="api-health"),
    path("contact/", views.contact, name="api-contact"),
    path("booking/", views.booking, name="api-booking"),
    path("newsletter/", views.newsletter, name="api-newsletter"),
]
