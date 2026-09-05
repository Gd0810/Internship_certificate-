from django.db import models


class BaseTemplate(models.Model):
    """Shared shape for certificate and offer-letter template packages."""

    track = models.ForeignKey(
        "company.InternshipTrack", on_delete=models.CASCADE, related_name="%(class)s_set",
        null=True, blank=True,
        help_text="Leave blank to use this as the site-wide default template.",
    )
    folder_path = models.CharField(
        max_length=300,
        help_text="Path (relative to MEDIA_ROOT/templates/<kind>/) where index.html and img/ live.",
    )
    is_active = models.BooleanField(default=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    def __str__(self):
        target = self.track.name if self.track_id else "Default"
        return f"{target} — {self.folder_path}"


class CertificateTemplate(BaseTemplate):
    pass


class OfferLetterTemplate(BaseTemplate):
    pass
