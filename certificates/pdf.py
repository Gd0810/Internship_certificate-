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
        return path
    return uri


import re

def _preprocess_html_for_pdf(html: str) -> str:
    """
    Ensures uploaded templates render cleanly on PDF export by resolving
    CSS variables and enforcing standard A4 page dimensions.
    """
    root_vars = {}
    for match in re.finditer(r"--([a-zA-Z0-9_-]+)\s*:\s*([^;}]+)", html):
        root_vars[match.group(1)] = match.group(2).strip()

    if root_vars:
        for var_name, var_val in root_vars.items():
            html = html.replace(f"var(--{var_name})", var_val)

    if "@page" not in html:
        is_cert = "certificate" in html.lower() and "offer" not in html.lower()
        page_spec = "size: A4 landscape; margin: 10mm;" if is_cert else "size: A4 portrait; margin: 12mm 16mm;"
        style_inject = f"<style>@page {{ {page_spec} }}</style>"
        if "</head>" in html:
            html = html.replace("</head>", f"{style_inject}</head>")
        else:
            html = f"{style_inject}{html}"

    return html


def _render_xhtml2pdf(html: str) -> bytes:
    from xhtml2pdf import pisa

    html = _preprocess_html_for_pdf(html)
    buffer = io.BytesIO()
    result = pisa.CreatePDF(html, dest=buffer, link_callback=_django_link_callback)
    if result.err:
        logger.error("xhtml2pdf reported %s error(s) while rendering.", result.err)
    return buffer.getvalue()


def html_to_pdf_bytes(html: str, base_url: str) -> bytes:
    """Render an HTML string to PDF bytes, preferring WeasyPrint when available."""
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
