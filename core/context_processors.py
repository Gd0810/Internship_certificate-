def site_meta(request):
    base_url = request.build_absolute_uri("/").rstrip("/")
    # In production with reverse proxies, ensure protocol matches https if SSL redirect is enabled
    from django.conf import settings
    if not settings.DEBUG and getattr(settings, "SECURE_SSL_REDIRECT", False):
        if base_url.startswith("http://"):
            base_url = "https://" + base_url[7:]

    return {
        "SITE_NAME": "Redback",
        "SITE_FULL_NAME": "Redback IT Solutions Private Limited",
        "SITE_TAGLINE": "Internship Programs, Practical Learning & Verified Certification",
        "SITE_URL": base_url,
        "SITE_TWITTER_HANDLE": "@redback_it",
        "DEFAULT_META_DESCRIPTION": (
            "Explore industry-grade technology internship programs with Redback IT Solutions. "
            "Master in-demand skills in Generative AI, Full Stack Development, Cloud Computing, "
            "and earn verifiable, shareable credentials."
        ),
        "DEFAULT_META_KEYWORDS": (
            "internship, tech internship, software development internship, Generative AI internship, "
            "Full Stack internship, cloud computing training, certificate verification, Redback IT Solutions"
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


