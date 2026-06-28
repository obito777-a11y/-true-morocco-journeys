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


class Booking(models.Model):
    """Stores every booking request submitted via the tour-detail form."""

    STATUS_CHOICES = [
        ("pending",   "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
    ]

    name        = models.CharField(max_length=100)
    email       = models.EmailField(db_index=True)
    phone       = models.CharField(max_length=20, blank=True, default="")
    tour_name   = models.CharField(max_length=200)
    travel_date = models.DateField()
    num_people  = models.PositiveIntegerField(default=1)
    message     = models.TextField(blank=True, default="")
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", db_index=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    notes       = models.TextField(blank=True, default="", verbose_name="Admin notes")

    class Meta:
        ordering = ["-submitted_at"]
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"

    def __str__(self):
        return f"{self.name} — {self.tour_name} ({self.travel_date})"


class ContactMessage(models.Model):
    """Stores every contact-form submission for admin review."""

    name         = models.CharField(max_length=100)
    email        = models.EmailField(db_index=True)
    phone        = models.CharField(max_length=20, blank=True, default="")
    subject      = models.CharField(max_length=200, blank=True, default="")
    message      = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-submitted_at"]
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"

    def __str__(self):
        return f"{self.name} — {self.subject or 'No subject'} ({self.submitted_at:%Y-%m-%d})"
