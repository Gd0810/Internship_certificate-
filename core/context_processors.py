def site_meta(request):
    base_url = request.build_absolute_uri("/").rstrip("/")
    # In production with reverse proxies, ensure protocol matches https if SSL redirect is enabled
    from django.conf import settings
    if not settings.DEBUG and getattr(settings, "SECURE_SSL_REDIRECT", False):
        if base_url.startswith("http://"):
            base_url = "https://" + base_url[7:]

    res = {
        "SITE_NAME": "Redback",
        "SITE_FULL_NAME": "Redback IT Solutions Private Limited",
        "SITE_TAGLINE": "Internship Programs, Practical Learning & Verified Certification",
        "SITE_URL": base_url,
        "SITE_TWITTER_HANDLE": "@redback_it",
        "DEFAULT_META_DESCRIPTION": (
            "Looking for online, free, or paid internship certificates in Vellore? "
            "Redback IT Solutions is a verified certificate provider offering the best computer certificate courses, "
            "software training certificates, and real-world IT company internships with authentic QR verification."
        ),
        "DEFAULT_META_KEYWORDS": (
            "online internship certificates in vellore, free internship certificates in vellore, "
            "paid internship certificates in vellore, internship certificate in vellore, "
            "best certificate courses in vellore, computer certificate courses in vellore, "
            "software training certificate in vellore, verified certificate provider in vellore, "
            "redback certificate vellore, it company internship with certificate in vellore, "
            "Redback IT Solutions, technology internship Vellore"
        ),
        "DEFAULT_OG_IMAGE": f"{base_url}/static/img/redback-og-banner.png",
    }

    if request.user.is_authenticated and request.user.is_staff:
        try:
            from core.models import ContactInquiry
            res["pending_inquiries_count"] = ContactInquiry.objects.filter(is_resolved=False).count()
        except Exception:
            res["pending_inquiries_count"] = 0

    return res


