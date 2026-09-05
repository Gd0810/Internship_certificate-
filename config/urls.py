from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("", include("core.urls")),
    path("accounts/", include("accounts.urls")),
    path("certificates/", include("certificates.urls")),
    path("payments/", include("payments.urls")),
    # Hidden company portal — the URL prefix is read from settings, not
    # hard-coded, and is never linked from any public-facing template.
    path(f"{settings.COMPANY_PORTAL_SLUG}/", include("company.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
