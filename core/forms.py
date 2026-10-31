from django import forms
from .models import ContactInquiry

INPUT_CLASSES = (
    "w-full rounded-xl border border-slate-200 bg-slate-50/50 px-4 py-3 "
    "text-sm text-[#151c27] placeholder:text-slate-400 focus:bg-white focus:border-[#bb0004] "
    "focus:outline-none focus:ring-3 focus:ring-[#bb0004]/10 transition-all duration-200"
)


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactInquiry
        fields = ["name", "email", "phone_number", "message"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": INPUT_CLASSES,
                "placeholder": "Enter your full name",
                "required": True,
            }),
            "email": forms.EmailInput(attrs={
                "class": INPUT_CLASSES,
                "placeholder": "name@example.com",
                "required": True,
            }),
            "phone_number": forms.TextInput(attrs={
                "class": INPUT_CLASSES,
                "placeholder": "+91 98765 43210",
                "required": True,
            }),
            "message": forms.Textarea(attrs={
                "class": INPUT_CLASSES,
                "rows": 4,
                "placeholder": "Write your query, preferred track, or internship questions...",
                "required": True,
            }),
        }
        labels = {
            "name": "Full Name",
            "email": "Email Address",
            "phone_number": "Phone Number",
            "message": "Your Message",
        }

