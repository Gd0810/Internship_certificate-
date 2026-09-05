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
    body_points_input = forms.CharField(
        widget=forms.Textarea(attrs={
            "class": INPUT, "rows": 4,
            "placeholder": "Enter each point on a new line, e.g.:\nIntroduction to mobile app ecosystems (Android, iOS)\nLearn screen navigation routes and styling\nSet up local development environment"
        }),
        required=False,
        label="Module Body Content / What You'll Do (1 point per line)",
        help_text="Each line entered here will become a bullet point in the student's task card."
    )
    deliverables_input = forms.CharField(
        widget=forms.Textarea(attrs={
            "class": INPUT, "rows": 3,
            "placeholder": "Enter each deliverable label on a new line, e.g.:\nLearning Notes Link (Google Docs or Notion)\nLinkedIn Post Link"
        }),
        required=False,
        label="Submission Deliverables (1 item per line)",
        help_text="Each line entered here will become a requested submission link field for the student."
    )

    class Meta:
        model = TaskModule
        fields = ["module_number", "title", "duration_info", "description", "order"]
        widgets = {
            "module_number": forms.NumberInput(attrs={"class": INPUT, "min": 1}),
            "title": forms.TextInput(attrs={"class": INPUT, "placeholder": "e.g. Mobile Development Fundamentals"}),
            "duration_info": forms.TextInput(attrs={"class": INPUT, "placeholder": "e.g. Day 1 – Day 5 · High priority"}),
            "description": forms.Textarea(attrs={"class": INPUT, "rows": 2, "placeholder": "Optional summary or overview"}),
            "order": forms.NumberInput(attrs={"class": INPUT}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["body_points_input"].initial = self.instance.body_points_text
            self.fields["deliverables_input"].initial = self.instance.deliverables_text

    def clean(self):
        cleaned_data = super().clean()
        bp_text = cleaned_data.get("body_points_input", "")
        bp_list = [line.strip() for line in bp_text.splitlines() if line.strip()]

        deliv_text = cleaned_data.get("deliverables_input", "")
        deliv_list = [line.strip() for line in deliv_text.splitlines() if line.strip()]

        self.cleaned_data["body_points"] = bp_list
        self.cleaned_data["deliverables"] = deliv_list
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.body_points = self.cleaned_data.get("body_points", [])
        instance.deliverables = self.cleaned_data.get("deliverables", [])
        if commit:
            instance.save()
        return instance


class TemplateUploadForm(forms.Form):
    track = forms.ModelChoiceField(
        queryset=InternshipTrack.objects.all(),
        required=False,
        empty_label="Global (All Tracks)",
        widget=forms.Select(attrs={"class": INPUT}),
        help_text="Select 'Global (All Tracks)' to automatically apply this template across all tracks.",
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
