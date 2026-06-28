"""
api/views.py — True Morocco Journeys API views.

Each view:
  • Validates input via a DRF serializer
  • Sends HTML emails via Django's email backend
  • Returns a consistent JSON envelope  { success: bool, message/error: str }
  • Logs every inbound request and outcome to tmj.log
"""
import logging
from datetime import datetime, timezone

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db import IntegrityError
from django.template.loader import render_to_string
from django_ratelimit.decorators import ratelimit
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import NewsletterSubscriber
from .serializers import BookingSerializer, ContactSerializer, NewsletterSerializer

logger = logging.getLogger("api")


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _get_client_ip(request) -> str:
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    return xff.split(",")[0].strip() if xff else request.META.get("REMOTE_ADDR", "unknown")


def _agency_ctx() -> dict:
    return {
        "agency_name": settings.AGENCY_NAME,
        "agency_phone": settings.AGENCY_PHONE,
        "agency_website": settings.AGENCY_WEBSITE,
    }


def _send_html_email(subject: str, to: list, template_name: str, context: dict) -> bool:
    ctx = {**_agency_ctx(), **context}
    try:
        html_body = render_to_string(f"emails/{template_name}", ctx)
        plain_body = "\n".join(
            line.strip() for line in html_body.split("\n")
            if line.strip() and not line.strip().startswith("<")
        )
        msg = EmailMultiAlternatives(
            subject=subject,
            body=plain_body,
            from_email=f"{settings.AGENCY_NAME} <{settings.EMAIL_HOST_USER}>",
            to=to,
        )
        msg.attach_alternative(html_body, "text/html")
        msg.send(fail_silently=False)
        logger.info("Email sent | to=%s | subject=%s", to, subject)
        return True
    except Exception as exc:
        logger.error("Email FAILED | to=%s | subject=%s | error=%s", to, subject, exc)
        return False


def _ok(message: str = "Success") -> Response:
    return Response({"success": True, "message": message}, status=200)


def _err(error: str, status: int = 400) -> Response:
    return Response({"success": False, "error": error}, status=status)


# ─── Health ────────────────────────────────────────────────────────────────────

@api_view(["GET"])
def health(request):
    return Response({
        "status": "ok",
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        "service": settings.AGENCY_NAME,
    }, status=200)


# ─── Contact ───────────────────────────────────────────────────────────────────

@api_view(["POST"])
@ratelimit(key="ip", rate="10/15m", method="POST", block=True)
def contact(request):
    ip = _get_client_ip(request)
    logger.info("Contact | ip=%s | data=%s", ip, request.data)

    serializer = ContactSerializer(data=request.data)
    if not serializer.is_valid():
        first_error = next(iter(serializer.errors.values()))[0]
        return _err(str(first_error))

    data = serializer.validated_data

    # ── FIX: build a descriptive subject from the submitted subject field ────
    submitted_subject = data.get("subject") or "General Enquiry"
    email_subject_admin = f"[{settings.AGENCY_NAME}] {submitted_subject} — from {data['name']}"
    email_subject_client = f"We received your message — {settings.AGENCY_NAME}"

    _send_html_email(
        subject=email_subject_admin,
        to=[settings.ADMIN_EMAIL],
        template_name="contact_admin.html",
        context=data,
    )
    _send_html_email(
        subject=email_subject_client,
        to=[data["email"]],
        template_name="contact_client.html",
        context=data,
    )

    logger.info("Contact OK | ip=%s | email=%s | subject=%s", ip, data["email"], submitted_subject)
    return _ok("Thank you! Your message has been sent. We'll reply within one business day.")


# ─── Booking ───────────────────────────────────────────────────────────────────

@api_view(["POST"])
@ratelimit(key="ip", rate="10/15m", method="POST", block=True)
def booking(request):
    ip = _get_client_ip(request)
    logger.info("Booking | ip=%s | data=%s", ip, request.data)

    serializer = BookingSerializer(data=request.data)
    if not serializer.is_valid():
        first_error = next(iter(serializer.errors.values()))[0]
        return _err(str(first_error))

    data = serializer.validated_data
    display_ctx = {**data, "travel_date_display": data["travel_date"].strftime("%B %d, %Y")}

    _send_html_email(
        subject=f"[{settings.AGENCY_NAME}] New Booking — {data['tour_name']} ({data['travel_date']})",
        to=[settings.ADMIN_EMAIL],
        template_name="booking_admin.html",
        context=display_ctx,
    )
    _send_html_email(
        subject=f"Booking Request Received — {data['tour_name']}",
        to=[data["email"]],
        template_name="booking_client.html",
        context=display_ctx,
    )

    logger.info("Booking OK | ip=%s | email=%s | tour=%s", ip, data["email"], data["tour_name"])
    return _ok(
        f"Your booking request for {data['tour_name']} has been received! "
        "We'll contact you within 24 hours to confirm availability."
    )


# ─── Newsletter ────────────────────────────────────────────────────────────────

@api_view(["POST"])
@ratelimit(key="ip", rate="10/15m", method="POST", block=True)
def newsletter(request):
    ip = _get_client_ip(request)
    logger.info("Newsletter | ip=%s | data=%s", ip, request.data)

    serializer = NewsletterSerializer(data=request.data)
    if not serializer.is_valid():
        first_error = next(iter(serializer.errors.values()))[0]
        return _err(str(first_error))

    email = serializer.validated_data["email"]

    try:
        subscriber, created = NewsletterSubscriber.objects.get_or_create(email=email)
        if not created:
            if not subscriber.is_active:
                subscriber.is_active = True
                subscriber.save(update_fields=["is_active"])
            return _ok("You're already subscribed to our newsletter!")
    except IntegrityError:
        return _ok("You're subscribed to our newsletter!")

    _send_html_email(
        subject=f"Welcome to {settings.AGENCY_NAME} — Your Moroccan Adventure Awaits!",
        to=[email],
        template_name="newsletter_welcome.html",
        context={"email": email},
    )

    logger.info("Newsletter OK | ip=%s | email=%s", ip, email)
    return _ok("You're subscribed! Welcome to our newsletter.")
