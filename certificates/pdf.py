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
            default_fallback = os.path.join(settings.MEDIA_ROOT, "templates", "offer_letter", "default-c43d595d", "img", basename)
            if os.path.isfile(default_fallback):
                return default_fallback
            seed_fallback = os.path.join(settings.MEDIA_ROOT, "templates", "offer_letter", "default-seed", "img", basename)
            if os.path.isfile(seed_fallback):
                return seed_fallback
            cert_fallback = os.path.join(settings.MEDIA_ROOT, "templates", "certificate", "default-cfe8f3a2", "img", basename)
            if os.path.isfile(cert_fallback):
                return cert_fallback
            cert_fallback_seed = os.path.join(settings.MEDIA_ROOT, "templates", "certificate", "default-seed", "img", basename)
            if os.path.isfile(cert_fallback_seed):
                return cert_fallback_seed
        return path

    # If requested image isn't found directly, try finding raster fallback in default folders
    if path.lower().endswith(".png") or path.lower().endswith(".jpg") or path.lower().endswith(".svg"):
        basename = os.path.basename(path)
        if basename.endswith(".svg"):
            basename = basename[:-4] + ".png"
        default_fallback = os.path.join(settings.MEDIA_ROOT, "templates", "offer_letter", "default-c43d595d", "img", basename)
        if os.path.isfile(default_fallback):
            return default_fallback
        seed_fallback = os.path.join(settings.MEDIA_ROOT, "templates", "offer_letter", "default-seed", "img", basename)
        if os.path.isfile(seed_fallback):
            return seed_fallback
        cert_fallback = os.path.join(settings.MEDIA_ROOT, "templates", "certificate", "default-cfe8f3a2", "img", basename)
        if os.path.isfile(cert_fallback):
            return cert_fallback
        cert_fallback_seed = os.path.join(settings.MEDIA_ROOT, "templates", "certificate", "default-seed", "img", basename)
        if os.path.isfile(cert_fallback_seed):
            return cert_fallback_seed

    return uri


import re

_poppins_registered = False


def _ensure_poppins_fonts():
    global _poppins_registered
    if _poppins_registered:
        return
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        import xhtml2pdf.context as x2p_ctx

        font_dir = os.path.join(settings.BASE_DIR, "static", "fonts")
        reg_path = os.path.join(font_dir, "Poppins-Regular.ttf")
        bold_path = os.path.join(font_dir, "Poppins-Bold.ttf")

        if not os.path.isfile(reg_path):
            alt_dir = os.path.join(settings.MEDIA_ROOT, "templates", "offer_letter", "default-c43d595d", "fonts")
            reg_path = os.path.join(alt_dir, "Poppins-Regular.ttf")
            bold_path = os.path.join(alt_dir, "Poppins-Bold.ttf")

        if os.path.isfile(reg_path) and os.path.isfile(bold_path):
            pdfmetrics.registerFont(TTFont("Poppins", reg_path))
            pdfmetrics.registerFont(TTFont("Poppins-Bold", bold_path))
            x2p_ctx.addMapping("poppins", 0, 0, "Poppins")
            x2p_ctx.addMapping("poppins", 1, 0, "Poppins-Bold")
            x2p_ctx.addMapping("poppins", 0, 1, "Poppins")
            x2p_ctx.addMapping("poppins", 1, 1, "Poppins-Bold")

            orig_init = x2p_ctx.pisaContext.__init__
            if not getattr(orig_init, "_poppins_patched", False):
                def patched_init(self, *args, **kwargs):
                    orig_init(self, *args, **kwargs)
                    self.fontList["poppins"] = "Poppins"
                patched_init._poppins_patched = True
                x2p_ctx.pisaContext.__init__ = patched_init

            _poppins_registered = True
            logger.info("Successfully registered Poppins fonts with ReportLab and xhtml2pdf.")
    except Exception as exc:
        logger.warning("Could not register Poppins font: %s", exc)


def _preprocess_html_for_pdf(html: str) -> str:
    """
    Ensures any uploaded company template (using flexbox, large margins, or custom CSS)
    renders cleanly on a single A4 PDF page by:
      1. Expanding all CSS variables (--var: val).
      2. Handling fallback resolution for image links.
      3. Forcing standard A4 page dimensions and non-zero margins (@page).
      4. Injecting CSS normalizers for font size, line-height, and element margins so content fits on 1 page.
    """
    _ensure_poppins_fonts()

    root_vars = {}
    for match in re.finditer(r"--([a-zA-Z0-9_-]+)\s*:\s*([^;}]+)", html):
        root_vars[match.group(1)] = match.group(2).strip()

    if root_vars:
        for var_name, var_val in root_vars.items():
            html = html.replace(f"var(--{var_name})", var_val)

    # Disable flexbox declarations that cause vertical stacking in xhtml2pdf
    html = re.sub(r'display:\s*flex;?', 'display: block;', html, flags=re.IGNORECASE)

    # Strip external Google Fonts stylesheets to avoid xhtml2pdf Windows temp file permission errors
    html = re.sub(r'<link[^>]*fonts\.googleapis\.com[^>]*>', '', html, flags=re.IGNORECASE)

    # Strip @media screen blocks so screen-only preview styles never affect the PDF
    html = re.sub(r'@media\s+screen\s*\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', '', html, flags=re.DOTALL | re.IGNORECASE)

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
        a4_style = "@page { size: A4 portrait; margin: 6mm 8mm 6mm 8mm; }"
        scale_override = """
<style>
  @page { size: A4 portrait; margin: 6mm 8mm 6mm 8mm; }
  html, body { background: #ffffff !important; margin: 0 !important; padding: 0 !important; }
  .page-wrap, .letter-wrap, .sheet, .letter { max-width: 100% !important; margin: 0 auto !important; padding: 0 !important; box-shadow: none !important; min-height: 0 !important; }
  img { max-width: 100% !important; }
  .sign-table { margin-bottom: 24px !important; }
  .acceptance-box { margin-top: 26px !important; }
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

    _ensure_poppins_fonts()
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
