import os
import sys
import io
import django

sys.path.insert(0, os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from certificates.models import OfferLetterTemplate, CertificateTemplate
from certificates.rendering import render_offer_letter, render_certificate
from certificates.pdf import html_to_pdf_bytes
from accounts.models import InternProfile
import fitz

os.makedirs("scratch", exist_ok=True)
artifact_scratch = r"C:\Users\redback\.gemini\antigravity-ide\brain\32b129b8-da8d-4017-9fbc-7960f374ca99\scratch"
os.makedirs(artifact_scratch, exist_ok=True)

profiles = InternProfile.objects.all()
print(f"Found {profiles.count()} intern profiles")

for p in profiles:
    track_name = p.track.name if p.track else "no_track"
    print(f"\n--- Testing profile: {p.full_name} ({p.user.username}), Track: {track_name} ---")
    
    # 1. Offer Letter
    offer_html = render_offer_letter(p)
    if offer_html:
        pdf_bytes = html_to_pdf_bytes(offer_html, base_url="http://127.0.0.1:8000")
        pdf_filename = f"scratch/offer_{p.user.id}.pdf"
        with open(pdf_filename, "wb") as f:
            f.write(pdf_bytes)
        
        doc = fitz.open(pdf_filename)
        num_pages = len(doc)
        print(f"Offer Letter PDF rendered: {len(pdf_bytes)} bytes | Pages: {num_pages}")
        assert num_pages == 1, f"Offer letter has {num_pages} pages, expected 1!"

    # 2. Certificate (temporarily set has_paid=True for testing)
    orig_paid = p.has_paid
    p.has_paid = True
    p.save()

    cert_html = render_certificate(p)
    if cert_html:
        c_pdf_bytes = html_to_pdf_bytes(cert_html, base_url="http://127.0.0.1:8000")
        c_pdf_filename = f"scratch/cert_{p.user.id}.pdf"
        with open(c_pdf_filename, "wb") as f:
            f.write(c_pdf_bytes)
        
        c_doc = fitz.open(c_pdf_filename)
        c_num_pages = len(c_doc)
        print(f"Certificate PDF rendered: {len(c_pdf_bytes)} bytes | Pages: {c_num_pages}")
        assert c_num_pages == 1, f"Certificate has {c_num_pages} pages, expected 1!"

    p.has_paid = orig_paid
    p.save()

print("\nALL PDF RENDERING VERIFICATIONS PASSED SUCCESSFULLY!")
