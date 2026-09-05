import random
import uuid
from django.conf import settings
from django.db import models
from django.core.validators import RegexValidator

mobile_validator = RegexValidator(
    regex=r"^\+?\d{7,15}$", message="Enter a valid mobile number (7–15 digits, optional +country code)."
)


def generate_unique_intern_id():
    """Generates a unique Intern ID in the format RBS/INT/XXXXXX (6 digits)."""
    while True:
        num = random.randint(100000, 999999)
        code = f"RBS/INT/{num}"
        if not InternProfile.objects.filter(intern_id=code).exists():
            return code


class InternProfile(models.Model):
    """Extends the built-in User model with the intern-specific fields."""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="intern_profile")
    full_name = models.CharField(max_length=150)
    college_name = models.CharField(max_length=200)
    degree = models.CharField(max_length=150)
    track = models.ForeignKey(
        "company.InternshipTrack", on_delete=models.PROTECT, related_name="enrolled_profiles"
    )
    mobile_number = models.CharField(max_length=16, validators=[mobile_validator])
    has_paid = models.BooleanField(default=False)
    intern_id = models.CharField(max_length=30, unique=True, null=True, blank=True, help_text="Unique Intern ID format: RBS/INT/XXXXXX")
    certificate_id = models.CharField(max_length=40, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.intern_id or self.user.email})"

    def save(self, *args, **kwargs):
        if not self.intern_id:
            self.intern_id = generate_unique_intern_id()
        super().save(*args, **kwargs)

    def generate_certificate_id(self):
        """Called once, right after a verified payment. Never regenerated afterwards."""
        if not self.certificate_id:
            self.certificate_id = f"CRT-{uuid.uuid4().hex[:10].upper()}"
            self.save(update_fields=["certificate_id"])
        return self.certificate_id

    @property
    def total_tasks(self):
        return self.track.task_modules.count()

    @property
    def completed_tasks(self):
        return self.task_progress.filter(is_completed=True).count()

    @property
    def progress_percent(self):
        total = self.total_tasks
        if not total:
            return 0
        return round((self.completed_tasks / total) * 100)

    @property
    def all_tasks_completed(self):
        total = self.total_tasks
        return total > 0 and self.completed_tasks == total
