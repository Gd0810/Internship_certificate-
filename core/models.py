from django.db import models


class ContactInquiry(models.Model):
    """Stores incoming messages from the public contact page and landing page."""
    name = models.CharField(max_length=150, help_text="Full name of the inquirer")
    email = models.EmailField(help_text="Email address for replies")
    phone_number = models.CharField(max_length=25, help_text="Contact phone number")
    message = models.TextField(help_text="Message or inquiry details")
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False, help_text="Mark whether this inquiry has been addressed")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Contact Inquiry"
        verbose_name_plural = "Contact Inquiries"

    def __str__(self):
        return f"{self.name} ({self.email}) — {self.created_at.strftime('%d %b %Y, %H:%M')}"
