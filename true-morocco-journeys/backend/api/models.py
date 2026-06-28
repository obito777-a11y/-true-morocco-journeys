"""
api/models.py — Database models for True Morocco Journeys API.
"""
from django.db import models


class NewsletterSubscriber(models.Model):
    """Stores newsletter subscribers. Email is unique — no duplicates allowed."""

    email = models.EmailField(unique=True, db_index=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-subscribed_at"]
        verbose_name = "Newsletter Subscriber"
        verbose_name_plural = "Newsletter Subscribers"

    def __str__(self):
        return self.email
