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


def _build_context(profile, is_certificate=False):
    date_str = profile.created_at.strftime("%d %B %Y")
    intern_id = profile.intern_id or ""
    cert_id = profile.certificate_id or intern_id
    full_name = profile.full_name or profile.user.get_full_name() or profile.user.username
    track_name = profile.track.name if profile.track else "Internship Program"
    college_name = profile.college_name or ""
    degree = profile.degree or ""

    return {
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


def render_certificate(profile):
    if not profile.has_paid:
        return None
    tpl = _resolve_template(CertificateTemplate, profile.track)
    if tpl is None:
        return None
    folder = _kind_root("certificate") / tpl.folder_path
    media_prefix = f"{settings.MEDIA_URL}templates/certificate/{tpl.folder_path}/"
    context = _build_context(profile, is_certificate=True)
    return render_template_html(folder, context, media_prefix)

