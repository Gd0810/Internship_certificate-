import logging

from django.contrib.auth.decorators import login_required
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect

from .pdf import html_to_pdf_bytes
from .rendering import render_offer_letter, render_certificate

logger = logging.getLogger("certificates")


def _profile_or_none(request):
    return getattr(request.user, "intern_profile", None)


PREVIEW_CONTAINER_STYLE = """
<style id="platform-preview-normalizer">
  html, body {
    margin: 0 auto !important;
    padding: 0 !important;
    box-sizing: border-box !important;
    background: #f8fafc !important;
    display: flex !important;
    justify-content: center !important;
    align-items: flex-start !important;
    min-height: 100vh !important;
  }
  .sheet, .certificate, .letter, .page-wrap, .letter-wrap, .cert-wrap {
    max-width: 100% !important;
    margin: 10px auto !important;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12) !important;
    background: #ffffff !important;
  }
</style>
"""


def _inject_preview_styles(html: str) -> str:
    if "</head>" in html:
        return html.replace("</head>", f"{PREVIEW_CONTAINER_STYLE}</head>")
    return f"{PREVIEW_CONTAINER_STYLE}{html}"


@login_required
@xframe_options_sameorigin
def offer_letter_preview(request):
    profile = _profile_or_none(request)
    if profile is None:
        return redirect("core:home")
    html = render_offer_letter(profile)
    if html is None:
        return HttpResponse(
            "<p style='font-family:sans-serif;padding:40px;color:#8a8a86;'>"
            "Offer letter template is not configured yet.</p>"
        )
    return HttpResponse(_inject_preview_styles(html))


@login_required
@xframe_options_sameorigin
def certificate_preview(request):
    profile = _profile_or_none(request)
    if profile is None:
        return redirect("core:home")
    if not profile.has_paid:
        return HttpResponseForbidden("Certificate is locked until payment is completed.")
    html = render_certificate(profile, request=request)
    if html is None:
        return HttpResponse(
            "<p style='font-family:sans-serif;padding:40px;color:#8a8a86;'>"
            "Certificate template is not configured yet.</p>"
        )

    response = HttpResponse(_inject_preview_styles(html))
    response["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"
    return response


@login_required
def offer_letter_download(request):
    profile = _profile_or_none(request)
    if profile is None:
        return redirect("core:home")
    html = render_offer_letter(profile)
    if html is None:
        return HttpResponse("Offer letter template is not configured yet.", status=503)

    pdf_bytes = html_to_pdf_bytes(html, base_url=request.build_absolute_uri("/"))
    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="offer-letter-{profile.user_id}.pdf"'
    return response


@login_required
def certificate_download(request):
    profile = _profile_or_none(request)
    if profile is None:
        return redirect("core:home")
    if not profile.has_paid:
        return HttpResponseForbidden("Certificate is locked until payment is completed.")

    base_url = request.build_absolute_uri("/")
    html = render_certificate(profile, request=request, base_url=base_url)
    if html is None:
        return HttpResponse("Certificate template is not configured yet.", status=503)

    pdf_bytes = html_to_pdf_bytes(html, base_url=request.build_absolute_uri("/"))
    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="certificate-{profile.certificate_id}.pdf"'
    return response


@login_required
def certificate_image(request):
    profile = _profile_or_none(request)
    if profile is None:
        return redirect("core:home")
    if not profile.has_paid:
        return HttpResponseForbidden("Certificate is locked until payment is completed.")

    base_url = request.build_absolute_uri("/")
    html = render_certificate(profile, request=request, base_url=base_url)
    if html is None:
        return HttpResponse("Certificate template is not configured yet.", status=503)

    pdf_bytes = html_to_pdf_bytes(html, base_url=base_url)
    try:
        try:
            import fitz
        except ImportError:
            import pymupdf as fitz
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        pix = doc[0].get_pixmap(dpi=150)
        png_bytes = pix.tobytes("png")
        response = HttpResponse(png_bytes, content_type="image/png")
        disp_type = "attachment" if request.GET.get("download") == "1" else "inline"
        filename = f"certificate-{profile.certificate_id or 'completion'}.png"
        response["Content-Disposition"] = f'{disp_type}; filename="{filename}"'
        response["Content-Length"] = str(len(png_bytes))
        return response
    except Exception as exc:
        logger.exception("Failed to render certificate PNG: %s", exc)
        return HttpResponse(f"Certificate image generation error: {exc}", status=500, content_type="text/plain")


