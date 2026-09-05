"""
PDF rendering with automatic engine fallback.

WeasyPrint gives the best fidelity (proper flexbox/modern CSS support) but
needs native GTK/Pango/Cairo libraries that aren't installed by default on
Windows. xhtml2pdf is pure Python (reportlab-based) and needs nothing extra,
but only understands a more basic, table-and-block CSS subset — which is why
the shipped certificate/offer-letter designs are built with tables rather
than flexbox (see the two default-seed templates for the pattern to follow
in your own uploaded designs, for maximum compatibility).

We try WeasyPrint first and silently fall back to xhtml2pdf if its native
libraries aren't available, so the app works out of the box on any machine.
Set PDF_ENGINE=weasyprint or PDF_ENGINE=xhtml2pdf in .env to force one.
"""
import io
import logging

from django.conf import settings

logger = logging.getLogger("certificates")

_weasyprint_available = None


def _try_weasyprint(html: str, base_url: str) -> bytes | None:
    global _weasyprint_available
    if _weasyprint_available is False:
        return None
    try:
        from weasyprint import HTML
        pdf_bytes = HTML(string=html, base_url=base_url).write_pdf()
        _weasyprint_available = True
        return pdf_bytes
    except Exception as exc:  # OSError (missing native libs), ImportError, etc.
        _weasyprint_available = False
        logger.warning("WeasyPrint unavailable (%s) — falling back to xhtml2pdf.", exc)
        return None


import os

def _django_link_callback(uri, rel):
    """
    Convert HTML URIs to absolute filesystem paths so xhtml2pdf can locate
    media (logos, signatures, seals, backgrounds) and static files.
    Includes fallback resolution for SVG / missing images.
    """
    if uri.startswith(settings.MEDIA_URL):
        path = os.path.join(settings.MEDIA_ROOT, uri[len(settings.MEDIA_URL):])
    elif uri.startswith(settings.STATIC_URL):
        path = os.path.join(settings.STATIC_ROOT, uri[len(settings.STATIC_URL):])
    else:
        clean_uri = uri.lstrip("/")
        path = os.path.join(settings.MEDIA_ROOT, clean_uri)
        if not os.path.isfile(path):
            path = os.path.join(settings.BASE_DIR, clean_uri)

    if os.path.isfile(path):
        # xhtml2pdf cannot render SVG directly. If SVG is requested, return raster PNG counterpart if available.
        if path.lower().endswith(".svg"):
            png_candidate = path[:-4] + ".png"
            if os.path.isfile(png_candidate):
                return png_candidate
            basename = os.path.basename(png_candidate)
            default_fallback = os.path.join(settings.MEDIA_ROOT, "templates", "offer_letter", "default-seed", "img", basename)
            if os.path.isfile(default_fallback):
                return default_fallback
            cert_fallback = os.path.join(settings.MEDIA_ROOT, "templates", "certificate", "default-seed", "img", basename)
            if os.path.isfile(cert_fallback):
                return cert_fallback
        return path

    # If requested image isn't found directly, try finding raster fallback in default seed folders
    if path.lower().endswith(".png") or path.lower().endswith(".jpg") or path.lower().endswith(".svg"):
        basename = os.path.basename(path)
        if basename.endswith(".svg"):
            basename = basename[:-4] + ".png"
        default_fallback = os.path.join(settings.MEDIA_ROOT, "templates", "offer_letter", "default-seed", "img", basename)
        if os.path.isfile(default_fallback):
            return default_fallback
        cert_fallback = os.path.join(settings.MEDIA_ROOT, "templates", "certificate", "default-seed", "img", basename)
        if os.path.isfile(cert_fallback):
            return cert_fallback

    return uri


import re

def _preprocess_html_for_pdf(html: str) -> str:
    """
    Ensures any uploaded company template (using flexbox, large margins, or custom CSS)
    renders cleanly on a single A4 PDF page by:
      1. Expanding all CSS variables (--var: val).
      2. Handling fallback resolution for image links.
      3. Forcing standard A4 page dimensions and non-zero margins (@page).
      4. Injecting CSS normalizers for font size, line-height, and element margins so content fits on 1 page.
    """
    root_vars = {}
    for match in re.finditer(r"--([a-zA-Z0-9_-]+)\s*:\s*([^;}]+)", html):
        root_vars[match.group(1)] = match.group(2).strip()

    if root_vars:
        for var_name, var_val in root_vars.items():
            html = html.replace(f"var(--{var_name})", var_val)

    # Disable flexbox declarations that cause vertical stacking in xhtml2pdf
    html = re.sub(r'display:\s*flex;?', 'display: block;', html, flags=re.IGNORECASE)

    is_cert = "certificate" in html.lower() and "offer" not in html.lower()

    if is_cert:
        a4_style = "@page { size: A4 landscape; margin: 8mm; }"
        scale_override = """
<style>
  @page { size: A4 landscape; margin: 8mm; }
  html, body { background: #ffffff !important; margin: 0 !important; padding: 0 !important; }
  .sheet, .certificate, .cert-wrap, body > div { max-width: 100% !important; margin: 0 auto !important; padding: 4px !important; box-shadow: none !important; }
  img { max-width: 100% !important; }
</style>
"""
    else:
        a4_style = "@page { size: A4 portrait; margin: 6mm 10mm 6mm 10mm; }"
        scale_override = """
<style>
  @page { size: A4 portrait; margin: 6mm 10mm 6mm 10mm; }
  html, body { background: #ffffff !important; margin: 0 !important; padding: 0 !important; font-size: 11.5px !important; }
  .page-wrap, .letter-wrap, .sheet, .letter { max-width: 100% !important; margin: 0 auto !important; padding: 0 !important; box-shadow: none !important; }
  .content { padding: 12px 18px 8px !important; }
  h1, h1.title { font-size: 20px !important; margin: 0 0 10px !important; }
  .meta-block, .subject, .salutation, p, p.body-text, .closing { font-size: 11.5px !important; line-height: 1.4 !important; margin-bottom: 8px !important; }
  .letterhead { margin-bottom: 12px !important; }
  .signature-block { margin-top: 8px !important; }
  .signature-block img.signature { height: 36px !important; }
  .doc-footer { margin-top: 10px !important; padding-top: 6px !important; }
  .bar-top, .bar-bottom { height: 12px !important; display: block !important; }
  .corner-bottom, img.corner-bottom { display: none !important; }
  img.logo { height: 40px !important; }
  img.seal { height: 44px !important; }
  img { max-width: 100% !important; }
</style>
"""

    if re.search(r"@page\s*\{[^}]*\}", html):
        html = re.sub(r"@page\s*\{[^}]*\}", a4_style, html)

    if "</head>" in html:
        html = html.replace("</head>", f"{scale_override}</head>")
    else:
        html = f"{scale_override}{html}"

    return html


def _render_xhtml2pdf(html: str) -> bytes:
    from xhtml2pdf import pisa

    buffer = io.BytesIO()
    result = pisa.CreatePDF(html, dest=buffer, link_callback=_django_link_callback)
    if result.err:
        logger.error("xhtml2pdf reported %s error(s) while rendering.", result.err)
    return buffer.getvalue()


def html_to_pdf_bytes(html: str, base_url: str) -> bytes:
    """Render an HTML string to PDF bytes, preferring WeasyPrint when available."""
    html = _preprocess_html_for_pdf(html)
    engine = getattr(settings, "PDF_ENGINE", "auto")

    if engine == "xhtml2pdf":
        return _render_xhtml2pdf(html)

    if engine == "weasyprint":
        from weasyprint import HTML
        return HTML(string=html, base_url=base_url).write_pdf()

    # auto: prefer WeasyPrint, fall back transparently.
    pdf_bytes = _try_weasyprint(html, base_url)
    if pdf_bytes is not None:
        return pdf_bytes
    return _render_xhtml2pdf(html)
