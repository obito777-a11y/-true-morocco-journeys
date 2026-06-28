"""
api/serializers.py — DRF serializers for True Morocco Journeys API.

All user input is validated here before any business logic runs.
"""
import re
from datetime import date

from rest_framework import serializers


# ─── Shared helpers ──────────────────────────────────────────────────────────

_PHONE_RE = re.compile(r"^[\+\d\s\-\(\)]{7,20}$")


def _validate_phone(value: str) -> str:
    """Accept international formats like +212 6XX XXX XXX."""
    if value and not _PHONE_RE.match(value):
        raise serializers.ValidationError(
            "Enter a valid phone number (7–20 digits, spaces, dashes, or +/() allowed)."
        )
    return value


# ─── Contact form ────────────────────────────────────────────────────────────

class ContactSerializer(serializers.Serializer):
    name = serializers.CharField(
        min_length=2,
        max_length=100,
        error_messages={
            "blank": "Name is required.",
            "min_length": "Name must be at least 2 characters.",
            "max_length": "Name must not exceed 100 characters.",
        },
    )
    email = serializers.EmailField(
        error_messages={"blank": "Email is required.", "invalid": "Enter a valid email address."}
    )
    phone = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=20,
        default="",
    )
    message = serializers.CharField(
        min_length=10,
        max_length=3000,
        error_messages={
            "blank": "Message is required.",
            "min_length": "Message must be at least 10 characters.",
            "max_length": "Message must not exceed 3000 characters.",
        },
    )

    def validate_name(self, value: str) -> str:
        return value.strip()

    def validate_email(self, value: str) -> str:
        return value.strip().lower()

    def validate_phone(self, value: str) -> str:
        return _validate_phone(value.strip())

    def validate_message(self, value: str) -> str:
        return value.strip()


# ─── Booking request ─────────────────────────────────────────────────────────

class BookingSerializer(serializers.Serializer):
    name = serializers.CharField(
        min_length=2,
        max_length=100,
        error_messages={"blank": "Name is required.", "min_length": "Name must be at least 2 characters."},
    )
    email = serializers.EmailField(
        error_messages={"blank": "Email is required.", "invalid": "Enter a valid email address."}
    )
    phone = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=20,
        default="",
    )
    tour_name = serializers.CharField(
        min_length=2,
        max_length=200,
        error_messages={"blank": "Tour name is required."},
    )
    travel_date = serializers.DateField(
        input_formats=["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"],
        error_messages={
            "invalid": "Enter a valid travel date (YYYY-MM-DD or DD/MM/YYYY).",
            "blank": "Travel date is required.",
        },
    )
    num_people = serializers.IntegerField(
        min_value=1,
        max_value=100,
        error_messages={
            "invalid": "Number of people must be a whole number.",
            "min_value": "At least 1 person is required.",
            "max_value": "For groups over 100 please contact us directly.",
        },
    )
    message = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=3000,
        default="",
    )

    def validate_name(self, value: str) -> str:
        return value.strip()

    def validate_email(self, value: str) -> str:
        return value.strip().lower()

    def validate_phone(self, value: str) -> str:
        return _validate_phone(value.strip())

    def validate_tour_name(self, value: str) -> str:
        return value.strip()

    def validate_travel_date(self, value: date) -> date:
        if value < date.today():
            raise serializers.ValidationError("Travel date must be in the future.")
        return value

    def validate_message(self, value: str) -> str:
        return value.strip()


# ─── Newsletter subscription ─────────────────────────────────────────────────

class NewsletterSerializer(serializers.Serializer):
    email = serializers.EmailField(
        error_messages={"blank": "Email is required.", "invalid": "Enter a valid email address."}
    )

    def validate_email(self, value: str) -> str:
        return value.strip().lower()
