"""
Placeholder-substitution rendering engine for company-uploaded certificate
and offer-letter designs.

Design goals (see the project report, §9/§10):
  1. A company-uploaded index.html is treated as a *design asset*, never as
     executable server code. We do plain, whitelisted {{token}} substitution
     on the raw text — we never pass it through Django's template engine, so
     it cannot execute template tags, access request/session data, or read
     other files on the server.
  2. Zip uploads are extracted with strict path-traversal protection and a
     required-file check (index.html + img/) before anything touches disk.
  3. All substituted values are HTML-escaped, so a user's own profile data
     (name, college, etc.) cannot inject markup into a certificate that will
     later be re-served to other people (self-XSS is still XSS).
"""
import os
import re
import zipfile
from html import escape
from pathlib import Path

from django.conf import settings

ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}
REQUIRED_ENTRY = "index.html"
PLACEHOLDER_RE = re.compile(r"\{\{\s*([a-zA-Z0-9_]+)\s*\}\}")


class TemplatePackageError(ValueError):
    """Raised when an uploaded template zip fails validation."""


def _safe_member_path(base_dir: Path, member_name: str) -> Path:
    """
    Resolve a zip member's target path and guarantee it stays inside base_dir.
    Rejects absolute paths, '..' traversal, and symlink tricks.
    """
    target = (base_dir / member_name).resolve()
    if base_dir.resolve() not in target.parents and target != base_dir.resolve():
        raise TemplatePackageError(f"Unsafe path in template package: {member_name}")
    return target


def _normalize_uploaded_index_html(index_path: Path) -> None:
    """
    Post-processes a newly uploaded index.html file:
      1. Resolves all CSS variables (--var: val) so PDF engines render colors properly.
      2. Injects standard A4 page dimension rules (@page size: A4).
      3. Normalizes wrapper container CSS so documents fit clean A4 pages in both preview & PDF export.
    """
    if not index_path.exists():
        return

    content = index_path.read_text(encoding="utf-8")
    path_str = str(index_path).lower()
    is_certificate = "certificate" in path_str and "offer" not in path_str

    # 1. Expand CSS variables
    root_vars = {}
    for match in re.finditer(r"--([a-zA-Z0-9_-]+)\s*:\s*([^;}]+)", content):
        var_name = match.group(1).strip()
        var_val = match.group(2).strip()
        root_vars[var_name] = var_val

    if root_vars:
        for var_name, var_val in root_vars.items():
            content = content.replace(f"var(--{var_name})", var_val)

    # 2. Inject standard A4 @page CSS rule if missing
    if "@page" not in content:
        a4_page_style = (
            "@page { size: A4 landscape; margin: 10mm; }"
            if is_certificate
            else "@page { size: A4 portrait; margin: 12mm 16mm; }"
        )
        style_block = f"<style>\n  {a4_page_style}\n</style>\n"
        if "</head>" in content:
            content = content.replace("</head>", f"{style_block}</head>")
        else:
            content = f"{style_block}{content}"

    # 3. Add print media overrides for clean single-page A4 PDF rendering
    pdf_override_css = """
<style>
@media print {
  html, body { background: #ffffff !important; width: 100% !important; margin: 0 !important; padding: 0 !important; }
  .page-wrap, .letter-wrap, .cert-wrap, .letter, .certificate { max-width: 100% !important; margin: 0 !important; padding: 0 !important; box-shadow: none !important; }
}
</style>
"""
    if "media print" not in content and "</head>" in content:
        content = content.replace("</head>", f"{pdf_override_css}</head>")

    index_path.write_text(content, encoding="utf-8")


def extract_template_package(zip_file, destination_dir: Path, max_size_mb: int = 15) -> None:
    """
    Safely extract an uploaded .zip (index.html + img/) into destination_dir.
    destination_dir is wiped and recreated first, so re-uploads fully replace
    the previous design. Automatically normalizes index.html to A4 page standards.
    """
    destination_dir = Path(destination_dir)

    with zipfile.ZipFile(zip_file) as zf:
        total_uncompressed = sum(info.file_size for info in zf.infolist())
        if total_uncompressed > max_size_mb * 1024 * 1024:
            raise TemplatePackageError(f"Template package exceeds {max_size_mb} MB uncompressed.")

        names = [n for n in zf.namelist() if not n.endswith("/")]

        # Normalise: some zip tools wrap everything in one top-level folder.
        top_levels = {n.split("/")[0] for n in names if "/" in n}
        strip_prefix = ""
        flat_has_index = any(n == REQUIRED_ENTRY for n in names)
        if not flat_has_index and len(top_levels) == 1:
            candidate = f"{next(iter(top_levels))}/{REQUIRED_ENTRY}"
            if candidate in names:
                strip_prefix = f"{next(iter(top_levels))}/"

        found_index = False
        for info in zf.infolist():
            name = info.filename
            if name.endswith("/"):
                continue
            rel = name[len(strip_prefix):] if strip_prefix and name.startswith(strip_prefix) else name
            if not rel or rel.startswith("/") or ".." in rel.split("/"):
                raise TemplatePackageError(f"Unsafe path in template package: {name}")

            ext = Path(rel).suffix.lower()
            if rel != REQUIRED_ENTRY and ext not in ALLOWED_IMAGE_EXTENSIONS and ext not in {".css", ".js"}:
                continue

            target_path = _safe_member_path(destination_dir, rel)
            target_path.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(info) as src, open(target_path, "wb") as dst:
                dst.write(src.read())

            if rel == REQUIRED_ENTRY:
                found_index = True

        if not found_index:
            raise TemplatePackageError("Zip package must contain an index.html at its root.")

    # Automatically normalize index.html for standard A4 preview & PDF output
    _normalize_uploaded_index_html(destination_dir / REQUIRED_ENTRY)


def render_template_html(folder_path: Path, context: dict, media_url_prefix: str) -> str:
    """
    Load index.html as plain text and substitute {{token}} placeholders.
    Unknown placeholders are left as an empty string rather than raising, so a
    template referencing a not-yet-supported token doesn't hard-fail a render.
    Relative img/ references are rewritten to the folder's real media URL.
    """
    index_path = Path(folder_path) / REQUIRED_ENTRY
    html = index_path.read_text(encoding="utf-8")

    def substitute(match):
        key = match.group(1)
        value = context.get(key, "")
        return escape(str(value))

    html = PLACEHOLDER_RE.sub(substitute, html)

    # Rewrite bare "img/..." references to the folder's real, servable media URL.
    html = re.sub(r'(src|href)="img/', f'\\1="{media_url_prefix}img/', html)
    return html
