from django.contrib import admin
from .models import ContactInquiry


@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "phone_number", "created_at", "is_resolved"]
    list_filter = ["is_resolved", "created_at"]
    search_fields = ["name", "email", "phone_number", "message"]
    list_editable = ["is_resolved"]
    readonly_fields = ["name", "email", "phone_number", "message", "created_at"]
    date_hierarchy = "created_at"

    fieldsets = (
        ("Contact Details", {
            "fields": ("name", "email", "phone_number", "created_at")
        }),
        ("Inquiry Message", {
            "fields": ("message",)
        }),
        ("Status & Resolution", {
            "fields": ("is_resolved",)
        }),
    )
