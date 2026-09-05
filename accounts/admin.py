from django.contrib import admin
from .models import InternProfile


@admin.register(InternProfile)
class InternProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "intern_id", "user", "track", "has_paid", "certificate_id", "created_at")
    list_filter = ("has_paid", "track")
    search_fields = ("full_name", "intern_id", "user__email", "certificate_id")
    readonly_fields = ("intern_id", "certificate_id")
