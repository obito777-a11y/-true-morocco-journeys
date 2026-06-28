"""
api/admin.py — Django admin configuration for True Morocco Explorer.
"""
from django.contrib import admin
from .models import Booking, ContactMessage, NewsletterSubscriber


# ── Booking ────────────────────────────────────────────────────────────────────

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display  = ("name", "email", "tour_name", "travel_date", "num_people", "status", "submitted_at")
    list_filter   = ("status", "travel_date", "submitted_at")
    search_fields = ("name", "email", "tour_name")
    readonly_fields = ("submitted_at",)
    ordering      = ("-submitted_at",)
    list_editable = ("status",)
    date_hierarchy = "submitted_at"

    fieldsets = (
        ("Client",  {"fields": ("name", "email", "phone")}),
        ("Tour",    {"fields": ("tour_name", "travel_date", "num_people", "message")}),
        ("Admin",   {"fields": ("status", "notes", "submitted_at")}),
    )

    actions = ["mark_confirmed", "mark_cancelled"]

    @admin.action(description="Mark selected bookings as Confirmed")
    def mark_confirmed(self, request, queryset):
        updated = queryset.update(status="confirmed")
        self.message_user(request, f"{updated} booking(s) marked as confirmed.")

    @admin.action(description="Mark selected bookings as Cancelled")
    def mark_cancelled(self, request, queryset):
        updated = queryset.update(status="cancelled")
        self.message_user(request, f"{updated} booking(s) marked as cancelled.")


# ── Contact Messages ───────────────────────────────────────────────────────────

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display  = ("name", "email", "subject", "submitted_at")
    list_filter   = ("submitted_at",)
    search_fields = ("name", "email", "subject", "message")
    readonly_fields = ("submitted_at",)
    ordering      = ("-submitted_at",)
    date_hierarchy = "submitted_at"


# ── Newsletter ─────────────────────────────────────────────────────────────────

@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display  = ("email", "subscribed_at", "is_active")
    list_filter   = ("is_active", "subscribed_at")
    search_fields = ("email",)
    readonly_fields = ("subscribed_at",)
    ordering      = ("-subscribed_at",)
    actions = ["deactivate_subscribers", "activate_subscribers"]

    @admin.action(description="Deactivate selected subscribers")
    def deactivate_subscribers(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} subscriber(s) deactivated.")

    @admin.action(description="Activate selected subscribers")
    def activate_subscribers(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} subscriber(s) activated.")
