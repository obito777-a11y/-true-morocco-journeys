"""
api/serializers.py — DRF serializers for True Morocco Journeys API.
All user input is validated here before any business logic runs.
"""
import re
from datetime import date

from rest_framework import serializers

_PHONE_RE = re.compile(r"^[\+\d\s\-\(\)]{7,20}$")


def _validate_phone(value: str) -> str:
    if value and not _PHONE_RE.match(value):
        raise serializers.ValidationError(
            "Enter a valid phone number (7–20 digits, spaces, dashes, or +/() allowed)."
        )
    return value


# ─── Contact form ─────────────────────────────────────────────────────────────
class ContactSerializer(serializers.Serializer):
    name = serializers.CharField(
        min_length=2, max_length=100,
        error_messages={"blank": "Name is required.", "min_length": "Name must be at least 2 characters."},
    )
    email = serializers.EmailField(
        error_messages={"blank": "Email is required.", "invalid": "Enter a valid email address."}
    )
    phone = serializers.CharField(required=False, allow_blank=True, max_length=20, default="")

    # ── FIX: subject field was missing ────────────────────────────────────────
    subject = serializers.CharField(required=False, allow_blank=True, max_length=200, default="")

    message = serializers.CharField(
        min_length=10, max_length=3000,
        error_messages={"blank": "Message is required.", "min_length": "Message must be at least 10 characters."},
    )

    def validate_name(self, value): return value.strip()
    def validate_email(self, value): return value.strip().lower()
    def validate_phone(self, value): return _validate_phone(value.strip())
    def validate_subject(self, value): return value.strip()
    def validate_message(self, value): return value.strip()


# ─── Booking request ──────────────────────────────────────────────────────────
class BookingSerializer(serializers.Serializer):
    name = serializers.CharField(min_length=2, max_length=100,
        error_messages={"blank": "Name is required."})
    email = serializers.EmailField(
        error_messages={"blank": "Email is required.", "invalid": "Enter a valid email address."})
    phone = serializers.CharField(required=False, allow_blank=True, max_length=20, default="")
    tour_name = serializers.CharField(min_length=2, max_length=200,
        error_messages={"blank": "Tour name is required."})
    travel_date = serializers.DateField(
        input_formats=["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"],
        error_messages={"invalid": "Enter a valid travel date (YYYY-MM-DD).", "blank": "Travel date is required."},
    )
    num_people = serializers.IntegerField(min_value=1, max_value=100,
        error_messages={"invalid": "Number of people must be a whole number.", "min_value": "At least 1 person required."})
    message = serializers.CharField(required=False, allow_blank=True, max_length=3000, default="")

    def validate_name(self, value): return value.strip()
    def validate_email(self, value): return value.strip().lower()
    def validate_phone(self, value): return _validate_phone(value.strip())
    def validate_tour_name(self, value): return value.strip()
    def validate_travel_date(self, value):
        if value < date.today():
            raise serializers.ValidationError("Travel date must be in the future.")
        return value
    def validate_message(self, value): return value.strip()


# ─── Newsletter ───────────────────────────────────────────────────────────────
class NewsletterSerializer(serializers.Serializer):
    email = serializers.EmailField(
        error_messages={"blank": "Email is required.", "invalid": "Enter a valid email address."})

    def validate_email(self, value): return value.strip().lower()
