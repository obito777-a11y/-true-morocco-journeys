"""
api/views.py — True Morocco Journeys API views.

Each view:
  • Validates input through a DRF serializer
  • Rate-limits the IP to 10 requests / 15 minutes
  • Sends HTML emails via Django's email backend
  • Returns a consistent JSON envelope
  • Logs every inbound request and outcome
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

# ─── Shared helpers ───────────────────────────────────────────────────────────

def _get_client_ip(request) -> str:
    """Extract the real client IP, respecting X-Forwarded-For from proxies."""
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")


def _agency_context() -> dict:
    """Return branding variables that every email template needs."""
    return {
        "agency_name": settings.AGENCY_NAME,
        "agency_phone": settings.AGENCY_PHONE,
        "agency_website": settings.AGENCY_WEBSITE,
    }


def _send_html_email(subject: str, to: list[str], template_name: str, context: dict) -> bool:
    """
    Render an HTML email template and send it.
    Returns True on success, False on any SMTP / rendering failure.
    The response is never crashed — failures are logged and swallowed.
    """
    ctx = {**_agency_context(), **context}
    try:
        html_body = render_to_string(f"emails/{template_name}", ctx)
        # Plain-text fallback strips HTML tags (very basic)
        plain_body = (
            f"{settings.AGENCY_NAME}\n\n"
            + "\n".join(
                line.strip()
                for line in html_body.split("\n")
                if line.strip() and not line.strip().startswith("<")
            )
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
    except Exception as exc:  # noqa: BLE001
        logger.error("Email FAILED | to=%s | subject=%s | error=%s", to, subject, exc)
        return False


def _ok(message: str = "Success") -> Response:
    return Response({"success": True, "message": message}, status=200)


def _err(error: str, status: int = 400) -> Response:
    return Response({"success": False, "error": error}, status=status)


# ─── Health check ─────────────────────────────────────────────────────────────

@api_view(["GET"])
def health(request):
    """GET /api/health/ — liveness probe."""
    logger.debug("Health check from %s", _get_client_ip(request))
    return Response(
        {
            "status": "ok",
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "service": settings.AGENCY_NAME,
        },
        status=200,
    )


# ─── Contact form ─────────────────────────────────────────────────────────────

@api_view(["POST"])
@ratelimit(key="ip", rate="10/15m", method="POST", block=True)
def contact(request):
    """
    POST /api/contact/
    Accepts: name, email, phone, message
    Sends notification to agency + confirmation to client.
    """
    ip = _get_client_ip(request)
    logger.info("Contact request | ip=%s | data=%s", ip, request.data)

    serializer = ContactSerializer(data=request.data)
    if not serializer.is_valid():
        logger.warning("Contact validation failed | ip=%s | errors=%s", ip, serializer.errors)
        first_error = next(iter(serializer.errors.values()))[0]
        return _err(str(first_error))

    data = serializer.validated_data

    # Email to agency owner
    _send_html_email(
        subject=f"New Contact Enquiry from {data['name']}",
        to=[settings.ADMIN_EMAIL],
        template_name="contact_admin.html",
        context=data,
    )

    # Confirmation email to client
    _send_html_email(
        subject=f"We received your message — {settings.AGENCY_NAME}",
        to=[data["email"]],
        template_name="contact_client.html",
        context=data,
    )

    logger.info("Contact processed successfully | ip=%s | email=%s", ip, data["email"])
    return _ok("Thank you! Your message has been sent. We'll reply within one business day.")


# ─── Booking request ──────────────────────────────────────────────────────────

@api_view(["POST"])
@ratelimit(key="ip", rate="10/15m", method="POST", block=True)
def booking(request):
    """
    POST /api/booking/
    Accepts: name, email, phone, tour_name, travel_date, num_people, message
    Sends detailed booking request to agency + confirmation to client.
    """
    ip = _get_client_ip(request)
    logger.info("Booking request | ip=%s | data=%s", ip, request.data)

    serializer = BookingSerializer(data=request.data)
    if not serializer.is_valid():
        logger.warning("Booking validation failed | ip=%s | errors=%s", ip, serializer.errors)
        first_error = next(iter(serializer.errors.values()))[0]
        return _err(str(first_error))

    data = serializer.validated_data

    # Format the date nicely for email templates
    display_ctx = {
        **data,
        "travel_date_display": data["travel_date"].strftime("%B %d, %Y"),
    }

    # Detailed booking notification to agency
    _send_html_email(
        subject=f"New Booking Request — {data['tour_name']} ({data['travel_date']})",
        to=[settings.ADMIN_EMAIL],
        template_name="booking_admin.html",
        context=display_ctx,
    )

    # Booking confirmation to client
    _send_html_email(
        subject=f"Booking Request Received — {data['tour_name']}",
        to=[data["email"]],
        template_name="booking_client.html",
        context=display_ctx,
    )

    logger.info(
        "Booking processed successfully | ip=%s | email=%s | tour=%s | date=%s",
        ip,
        data["email"],
        data["tour_name"],
        data["travel_date"],
    )
    return _ok(
        f"Your booking request for {data['tour_name']} has been received! "
        "We'll contact you within 24 hours to confirm availability."
    )


# ─── Newsletter subscription ──────────────────────────────────────────────────

@api_view(["POST"])
@ratelimit(key="ip", rate="10/15m", method="POST", block=True)
def newsletter(request):
    """
    POST /api/newsletter/
    Accepts: email
    Saves subscriber to DB and sends a welcome email.
    """
    ip = _get_client_ip(request)
    logger.info("Newsletter request | ip=%s | data=%s", ip, request.data)

    serializer = NewsletterSerializer(data=request.data)
    if not serializer.is_valid():
        logger.warning("Newsletter validation failed | ip=%s | errors=%s", ip, serializer.errors)
        first_error = next(iter(serializer.errors.values()))[0]
        return _err(str(first_error))

    email = serializer.validated_data["email"]

    # Save subscriber (handle duplicates gracefully)
    try:
        subscriber, created = NewsletterSubscriber.objects.get_or_create(email=email)
        if not created:
            if not subscriber.is_active:
                # Re-activate a previously unsubscribed address
                subscriber.is_active = True
                subscriber.save(update_fields=["is_active"])
                logger.info("Newsletter re-subscribed | ip=%s | email=%s", ip, email)
            else:
                logger.info("Newsletter already subscribed | ip=%s | email=%s", ip, email)
                # Still success — don't leak whether the address exists
                return _ok("You're subscribed to our newsletter!")
    except IntegrityError:
        # Race condition — another request created the record between get and create
        logger.warning("Newsletter IntegrityError (race) | ip=%s | email=%s", ip, email)
        return _ok("You're subscribed to our newsletter!")

    # Welcome email to subscriber
    _send_html_email(
        subject=f"Welcome to {settings.AGENCY_NAME} — Your Moroccan Adventure Awaits!",
        to=[email],
        template_name="newsletter_welcome.html",
        context={"email": email},
    )

    logger.info("Newsletter subscribed successfully | ip=%s | email=%s", ip, email)
    return _ok("You're subscribed! Welcome to our newsletter.")
