from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator


class InternshipTrack(models.Model):
    """A company-defined internship program that users can enroll in."""

    name = models.CharField(max_length=140)
    slug = models.SlugField(max_length=160, unique=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)],
        help_text="Amount charged to unlock the certificate for this track.",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)[:150]
            slug = base
            n = 1
            while InternshipTrack.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                n += 1
                slug = f"{base}-{n}"
            self.slug = slug
        super().save(*args, **kwargs)


class TaskModule(models.Model):
    """One learning/task unit within a track. Order controls display sequence."""

    track = models.ForeignKey(InternshipTrack, on_delete=models.CASCADE, related_name="task_modules")
    module_number = models.PositiveIntegerField(default=1, help_text="Module sequence number, e.g. 1 for Module 1")
    title = models.CharField(max_length=160)
    duration_info = models.CharField(max_length=160, blank=True, default="Day 1 – Day 5 · High priority")
    description = models.TextField(blank=True, help_text="General summary or notes")
    body_points = models.JSONField(default=list, blank=True, help_text="List of bullet points for 'What You'll Do'")
    deliverables = models.JSONField(default=list, blank=True, help_text="List of deliverable field labels expected from interns")
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["track", "module_number", "order", "id"]

    def __str__(self):
        return f"{self.track.name} · Module {self.module_number}: {self.title}"

    @property
    def body_points_text(self):
        if isinstance(self.body_points, list):
            return "\n".join(self.body_points)
        return str(self.body_points or "")

    @property
    def deliverables_text(self):
        if isinstance(self.deliverables, list):
            return "\n".join(self.deliverables)
        return str(self.deliverables or "")


class UserTaskProgress(models.Model):
    """Tracks whether a given intern has completed a given task module and stores submission links."""

    profile = models.ForeignKey(
        "accounts.InternProfile", on_delete=models.CASCADE, related_name="task_progress"
    )
    task = models.ForeignKey(TaskModule, on_delete=models.CASCADE, related_name="progress_records")
    is_completed = models.BooleanField(default=False)
    submission_data = models.JSONField(default=dict, blank=True, help_text="Submitted deliverable links/text from intern")
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("profile", "task")

    def __str__(self):
        state = "done" if self.is_completed else "pending"
        return f"{self.profile} — {self.task.title} ({state})"
