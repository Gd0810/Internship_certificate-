from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("profile", "track", "amount", "status", "created_at")
    list_filter = ("status", "track")
    search_fields = ("razorpay_order_id", "razorpay_payment_id")
