from django import forms
from .models import InternshipTrack, TaskModule

INPUT = (
    "icp-input w-full rounded-lg border border-[--c-border] bg-white px-4 py-2.5 "
    "text-[--c-ink] focus:border-[--c-accent] focus:outline-none focus:ring-2 "
    "focus:ring-[--c-accent]/20 transition"
)


class TrackForm(forms.ModelForm):
    class Meta:
        model = InternshipTrack
        fields = ["name", "description", "price", "is_active"]
        widgets = {
            "name": forms.TextInput(attrs={"class": INPUT}),
            "description": forms.Textarea(attrs={"class": INPUT, "rows": 4}),
            "price": forms.NumberInput(attrs={"class": INPUT, "step": "0.01"}),
            "is_active": forms.CheckboxInput(attrs={"class": "icp-checkbox"}),
        }


class TaskModuleForm(forms.ModelForm):
    class Meta:
        model = TaskModule
        fields = ["title", "description", "order"]
        widgets = {
            "title": forms.TextInput(attrs={"class": INPUT}),
            "description": forms.Textarea(attrs={"class": INPUT, "rows": 3}),
            "order": forms.NumberInput(attrs={"class": INPUT}),
        }


class TemplateUploadForm(forms.Form):
    track = forms.ModelChoiceField(
        queryset=InternshipTrack.objects.all(), required=False,
        widget=forms.Select(attrs={"class": INPUT}),
        help_text="Leave blank to set this as the site-wide default.",
    )
    package = forms.FileField(
        widget=forms.ClearableFileInput(attrs={"class": INPUT, "accept": ".zip"}),
        help_text="A .zip containing index.html at its root and an img/ folder.",
    )

    def clean_package(self):
        f = self.cleaned_data["package"]
        if not f.name.lower().endswith(".zip"):
            raise forms.ValidationError("Please upload a .zip file.")
        return f
