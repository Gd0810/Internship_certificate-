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


def render_offer_letter(profile):
    tpl = _resolve_template(OfferLetterTemplate, profile.track)
    if tpl is None:
        return None
    folder = _kind_root("offer_letter") / tpl.folder_path
    media_prefix = f"{settings.MEDIA_URL}templates/offer_letter/{tpl.folder_path}/"
    context = {
        "user_name": profile.full_name,
        "intern_id": profile.intern_id or "",
        "college_name": profile.college_name,
        "degree": profile.degree,
        "track_name": profile.track.name,
        "start_date": profile.created_at.strftime("%d %B %Y"),
        "date": profile.created_at.strftime("%d %B %Y"),
    }
    return render_template_html(folder, context, media_prefix)


def render_certificate(profile):
    if not profile.has_paid:
        return None
    tpl = _resolve_template(CertificateTemplate, profile.track)
    if tpl is None:
        return None
    folder = _kind_root("certificate") / tpl.folder_path
    media_prefix = f"{settings.MEDIA_URL}templates/certificate/{tpl.folder_path}/"
    context = {
        "user_name": profile.full_name,
        "intern_id": profile.intern_id or "",
        "test_name": profile.track.name,
        "track_name": profile.track.name,
        "score": "Pass",
        "date": profile.created_at.strftime("%d %B %Y"),
        "certificate_id": profile.certificate_id or "",
    }
    return render_template_html(folder, context, media_prefix)
