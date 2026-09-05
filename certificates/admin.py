from django.contrib import admin
from .models import CertificateTemplate, OfferLetterTemplate


@admin.register(CertificateTemplate)
class CertificateTemplateAdmin(admin.ModelAdmin):
    list_display = ("track", "folder_path", "is_active", "uploaded_at")
    list_filter = ("is_active",)


@admin.register(OfferLetterTemplate)
class OfferLetterTemplateAdmin(admin.ModelAdmin):
    list_display = ("track", "folder_path", "is_active", "uploaded_at")
    list_filter = ("is_active",)
