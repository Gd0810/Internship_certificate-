from django.db import models


class Payment(models.Model):
    STATUS_CHOICES = [
        ("created", "Created"),
        ("paid", "Paid"),
        ("failed", "Failed"),
    ]

    profile = models.ForeignKey("accounts.InternProfile", on_delete=models.CASCADE, related_name="payments")
    track = models.ForeignKey("company.InternshipTrack", on_delete=models.PROTECT, related_name="payments")
    razorpay_order_id = models.CharField(max_length=64, unique=True)
    razorpay_payment_id = models.CharField(max_length=64, blank=True)
    razorpay_signature = models.CharField(max_length=128, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="created")
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.profile} — {self.track.name} — {self.status}"
