from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

from company.models import InternshipTrack
from .models import InternProfile, mobile_validator

User = get_user_model()

INPUT_CLASSES = (
    "icp-input w-full rounded-lg border border-[--c-border] bg-white px-4 py-2.5 "
    "text-[--c-ink] placeholder:text-[--c-muted] focus:border-[--c-accent] "
    "focus:outline-none focus:ring-2 focus:ring-[--c-accent]/20 transition"
)


class RegistrationForm(forms.Form):
    full_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={"class": INPUT_CLASSES, "placeholder": "Full name"}))
    college_name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={"class": INPUT_CLASSES, "placeholder": "College / university name"}))
    degree = forms.CharField(max_length=150, widget=forms.TextInput(attrs={"class": INPUT_CLASSES, "placeholder": "Degree, e.g. B.Tech CSE"}))
    track = forms.ModelChoiceField(
        queryset=InternshipTrack.objects.filter(is_active=True),
        widget=forms.Select(attrs={"class": INPUT_CLASSES}),
        empty_label="Select an internship track",
    )
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": INPUT_CLASSES, "placeholder": "you@example.com"}))
    mobile_number = forms.CharField(
        max_length=16, validators=[mobile_validator],
        widget=forms.TextInput(attrs={"class": INPUT_CLASSES, "placeholder": "+91 98765 43210"}),
    )
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": INPUT_CLASSES, "placeholder": "Password"}))
    re_enter_password = forms.CharField(widget=forms.PasswordInput(attrs={"class": INPUT_CLASSES, "placeholder": "Re-enter password"}))

    def clean_email(self):
        email = self.cleaned_data["email"].lower().strip()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email

    def clean(self):
        cleaned = super().clean()
        pw, pw2 = cleaned.get("password"), cleaned.get("re_enter_password")
        if pw and pw2 and pw != pw2:
            self.add_error("re_enter_password", "Passwords do not match.")
        if pw:
            from django.contrib.auth.password_validation import validate_password
            try:
                validate_password(pw)
            except ValidationError as exc:
                self.add_error("password", exc)
        return cleaned


class StyledAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({"class": INPUT_CLASSES, "placeholder": "Email", "autofocus": True})
        self.fields["password"].widget.attrs.update({"class": INPUT_CLASSES, "placeholder": "Password"})
