"""
api/admin.py — Django admin configuration for True Morocco Journeys API.
"""
from django.contrib import admin
from .models import NewsletterSubscriber


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "subscribed_at", "is_active")
    list_filter = ("is_active", "subscribed_at")
    search_fields = ("email",)
    readonly_fields = ("subscribed_at",)
    ordering = ("-subscribed_at",)
    actions = ["deactivate_subscribers", "activate_subscribers"]

    @admin.action(description="Deactivate selected subscribers")
    def deactivate_subscribers(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} subscriber(s) deactivated.")

    @admin.action(description="Activate selected subscribers")
    def activate_subscribers(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} subscriber(s) activated.")
