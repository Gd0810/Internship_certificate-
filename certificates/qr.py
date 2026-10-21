import base64
import io
import logging
import re
from pathlib import Path

from django.conf import settings
from django.urls import reverse

import urllib.parse
from urllib.parse import quote

logger = logging.getLogger("certificates")


def get_local_lan_ip() -> str:
    """Determine the LAN IPv4 address of this machine (e.g. 192.168.1.127)."""
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def get_verification_url(profile, request=None, base_url=None) -> str:
    """Build the public verification URL for the student's profile."""
    intern_id = getattr(profile, "intern_id", "") or ""
    encoded_id = quote(intern_id, safe="")
    verify_path = f"/verify/?intern_id={encoded_id}"
    try:
        verify_path = f"{reverse('core:verify')}?intern_id={encoded_id}"
    except Exception:
        pass

    custom_public_base = getattr(settings, "CERTIFICATE_VERIFY_BASE_URL", "").strip()
    if custom_public_base:
        return f"{custom_public_base.rstrip('/')}{verify_path}"

    url = ""
    if request is not None:
        try:
            url = request.build_absolute_uri(verify_path)
        except Exception as exc:
            logger.debug("Failed build_absolute_uri from request: %s", exc)
    elif base_url:
        url = f"{base_url.rstrip('/')}{verify_path}"
    else:
        url = f"http://127.0.0.1:8000{verify_path}"

    # If the URL hostname is loopback/localhost, replace it with the machine's
    # actual Wi-Fi/LAN IP so phones scanning the QR code can open the link!
    try:
        parsed = urllib.parse.urlparse(url)
        if parsed.hostname in ("127.0.0.1", "localhost", "0.0.0.0"):
            lan_ip = get_local_lan_ip()
            port = f":{parsed.port}" if parsed.port else ":8000"
            netloc = f"{lan_ip}{port}"
            url = urllib.parse.urlunparse(parsed._replace(netloc=netloc))
    except Exception as exc:
        logger.debug("Failed LAN IP resolution: %s", exc)

    return url


def generate_qr_code(profile, request=None, base_url=None) -> dict:
    """
    Dynamically generates a QR code image that encodes the student's
    verification URL (showing their verified credentials, completed modules, etc.).

    Returns a dict with:
      - verify_url: Target URL encoded in the QR code
      - qr_code_url: Media URL path (e.g. /media/qr_codes/qr_RBS_INT_123456.png)
      - qr_code_data_uri: Inlined base64 PNG data URI
      - qr_code_path: Local filesystem path where the PNG is stored
    """
    intern_id = getattr(profile, "intern_id", "") or "STUDENT"
    verify_url = get_verification_url(profile, request=request, base_url=base_url)

    try:
        import qrcode

        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=6,
            border=2,
        )
        qr.add_data(verify_url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="#151c27", back_color="#ffffff")

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        png_bytes = buf.getvalue()
        data_uri = f"data:image/png;base64,{base64.b64encode(png_bytes).decode('ascii')}"
    except Exception as exc:
        logger.warning("Local qrcode generation error: %s - falling back to web QR endpoint", exc)
        import urllib.parse
        encoded_verify = urllib.parse.quote(verify_url, safe="")
        qr_web_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={encoded_verify}&color=15-28-39"
        return {
            "verify_url": verify_url,
            "qr_code_url": qr_web_url,
            "qr_code_data_uri": qr_web_url,
            "qr_code_path": "",
        }

    # Save to disk under MEDIA_ROOT/qr_codes/ (safe fallback to data_uri if disk error)
    clean_id = re.sub(r"[^a-zA-Z0-9_-]", "_", intern_id)
    filename = f"qr_{clean_id}.png"
    qr_path_str = ""
    qr_url = data_uri
    try:
        qr_dir = Path(settings.MEDIA_ROOT) / "qr_codes"
        qr_dir.mkdir(parents=True, exist_ok=True)
        qr_path = qr_dir / filename
        qr_path.write_bytes(png_bytes)
        qr_path_str = str(qr_path)
        media_prefix = getattr(settings, "MEDIA_URL", "/media/")
        if not media_prefix.startswith("/"):
            media_prefix = "/" + media_prefix
        if not media_prefix.endswith("/"):
            media_prefix += "/"
        qr_url = f"{media_prefix}qr_codes/{filename}"
    except Exception as exc:
        logger.warning("Could not persist QR file to disk: %s", exc)

    return {
        "verify_url": verify_url,
        "qr_code_url": qr_url,
        "qr_code_data_uri": data_uri,
        "qr_code_path": qr_path_str,
    }
