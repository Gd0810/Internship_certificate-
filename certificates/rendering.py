"""Helpers that pick the right template for a track and build the context."""
from pathlib import Path
from django.conf import settings
from django.urls import reverse

from .models import CertificateTemplate, OfferLetterTemplate
from .template_engine import render_template_html


def _resolve_template(model, track):
    tpl = model.objects.filter(track=track, is_active=True).first()
    if tpl is None:
        tpl = model.objects.filter(track__isnull=True, is_active=True).first()
    return tpl


def _kind_root(kind):
    return Path(settings.CERT_TEMPLATE_ROOT) / kind


def _build_context(profile, is_certificate=False, request=None, base_url=None):
    date_str = profile.created_at.strftime("%d %B %Y")
    intern_id = profile.intern_id or ""
    if not intern_id and hasattr(profile, "save"):
        from accounts.models import generate_unique_intern_id
        profile.intern_id = generate_unique_intern_id()
        profile.save(update_fields=["intern_id"])
        intern_id = profile.intern_id

    cert_id = profile.certificate_id or intern_id
    full_name = profile.full_name or profile.user.get_full_name() or profile.user.username
    track_name = profile.track.name if profile.track else "Internship Program"
    college_name = profile.college_name or ""
    degree = profile.degree or ""

    qr_code_html = ""
    qr_url = ""
    qr_data_uri = ""
    verify_url = ""

    if is_certificate:
        try:
            from .qr import generate_qr_code
            qr_info = generate_qr_code(profile, request=request, base_url=base_url)
            verify_url = qr_info["verify_url"]
            qr_url = qr_info["qr_code_url"]
            qr_data_uri = qr_info["qr_code_data_uri"]
            qr_code_html = (
                f'<table style="width: 80px; margin: 0 auto; border: 1px solid #c8c2b5; border-collapse: collapse; background: #ffffff;">'
                f'<tr><td style="padding: 3px; text-align: center; border: none; width: 80px;">'
                f'<img src="{qr_data_uri}" width="72" height="72" alt="Verification QR Code" style="width: 72px; height: 72px; display: block; margin: 0 auto;">'
                f'</td></tr></table>'
                f'<div style="font-family:\'DejaVu Sans\', sans-serif; font-size: 10px; color: #8a8a86; margin-top: 4px; letter-spacing: 0.5px;">Scan to Verify</div>'
            )
        except Exception as exc:
            import logging
            logging.getLogger("certificates").warning("Failed generating certificate QR code: %s", exc)

    return {
        # Profile & User object references for dotted attribute lookups
        "profile": profile,
        "user": profile.user,
        # Direct dotted keys
        "profile.intern_id": intern_id,
        "profile.certificate_id": cert_id,
        "profile.full_name": full_name,
        "profile.user_name": full_name,
        "profile.college_name": college_name,
        "profile.degree": degree,
        "profile.track": track_name,
        "profile.track.name": track_name,
        "profile.track_name": track_name,
        "profile.qr_code_url": qr_data_uri or qr_url,
        "profile.qr_code_data_uri": qr_data_uri or qr_url,
        "profile.qr_code_file_url": qr_url,
        "profile.verify_url": verify_url,
        # QR Code and Verification URLs
        "verify_url": verify_url,
        "verification_url": verify_url,
        "qr_code_url": qr_data_uri or qr_url,
        "qr_code_data_uri": qr_data_uri or qr_url,
        "qr_code_file_url": qr_url,
        "qr_code": qr_code_html,
        "qr_code_img": qr_code_html,
        "qr_code_html": qr_code_html,
        # Candidate name synonyms
        "user_name": full_name,
        "student_name": full_name,
        "name": full_name,
        "candidate_name": full_name,
        "full_name": full_name,
        # Intern ID synonyms
        "intern_id": intern_id,
        "internship_id": intern_id,
        "id": intern_id,
        "roll_no": intern_id,
        # Institution synonyms
        "college_name": college_name,
        "college": college_name,
        "institution": college_name,
        "university": college_name,
        # Academic synonyms
        "degree": degree,
        "branch": degree,
        "course": degree,
        # Track/Role synonyms
        "track_name": track_name,
        "track": track_name,
        "program": track_name,
        "domain": track_name,
        "test_name": track_name,
        "role": track_name,
        "position": track_name,
        # Date synonyms
        "start_date": date_str,
        "joining_date": date_str,
        "date": date_str,
        "issue_date": date_str,
        "today": date_str,
        # Document ID & Evaluation
        "certificate_id": cert_id,
        "cert_id": cert_id,
        "doc_id": cert_id,
        "score": "Pass",
    }


def render_offer_letter(profile):
    tpl = _resolve_template(OfferLetterTemplate, profile.track)
    if tpl is None:
        return None
    folder = _kind_root("offer_letter") / tpl.folder_path
    media_prefix = f"{settings.MEDIA_URL}templates/offer_letter/{tpl.folder_path}/"
    context = _build_context(profile, is_certificate=False)
    return render_template_html(folder, context, media_prefix)


def render_certificate(profile, request=None, base_url=None):
    if not profile.has_paid:
        return None
    tpl = _resolve_template(CertificateTemplate, profile.track)
    if tpl is None:
        return None
    folder = _kind_root("certificate") / tpl.folder_path
    media_prefix = f"{settings.MEDIA_URL}templates/certificate/{tpl.folder_path}/"
    context = _build_context(profile, is_certificate=True, request=request, base_url=base_url)
    return render_template_html(folder, context, media_prefix)


