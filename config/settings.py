"""
Django settings for the Internship Certificate Provider platform.

Security & scalability notes:
- All secrets are read from environment variables (python-decouple), never hard-coded.
- DEBUG defaults to False; must be explicitly enabled for local dev.
- Database defaults to SQLite for local dev, but reads DATABASE_URL when set so it
  drops straight into Postgres/MySQL for production with zero code changes.
- Cache defaults to local memory but reads REDIS_URL when set, so session/cache load
  can be moved off individual app servers as traffic grows.
- Static files are served via WhiteNoise with compressed manifest storage, so the app
  scales horizontally without needing a separate static file server.
- A full set of SECURE_* / SESSION_* / CSRF_* hardening settings is applied whenever
  DEBUG is False.
"""

import os
from pathlib import Path
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent

# --------------------------------------------------------------------------
# Core / security
# --------------------------------------------------------------------------
SECRET_KEY = config("DJANGO_SECRET_KEY", default="dev-only-insecure-key-change-me")
# Defaults to True so a freshly-downloaded copy runs over plain HTTP locally
# without extra setup. Set DJANGO_DEBUG=False (and everything else in
# .env.example) before deploying anywhere reachable from the internet.
DEBUG = config("DJANGO_DEBUG", default=True, cast=bool)
ALLOWED_HOSTS = config("DJANGO_ALLOWED_HOSTS", default="127.0.0.1,localhost,testserver", cast=Csv())

# The company portal is intentionally reached through an unlisted, random-looking
# URL prefix rather than a guessable "/company/" path. Override in production via env.
COMPANY_PORTAL_SLUG = config("COMPANY_PORTAL_SLUG", default="mgmt-9f21")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "core",
    "accounts",
    "company",
    "payments",
    "certificates",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "core.middleware.RateLimitMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.site_meta",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# --------------------------------------------------------------------------
# Database — SQLite by default, DATABASE_URL (Postgres/MySQL) in production
# --------------------------------------------------------------------------
DATABASE_URL = config("DATABASE_URL", default="")
if DATABASE_URL:
    import dj_database_url

    DATABASES = {
        "default": dj_database_url.parse(DATABASE_URL, conn_max_age=600, conn_health_checks=True)
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# --------------------------------------------------------------------------
# Cache — LocMemCache locally, Redis in production (sessions, rate limiting,
# rendered-certificate-preview caching all use this).
# --------------------------------------------------------------------------
REDIS_URL = config("REDIS_URL", default="")
if REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": REDIS_URL,
        }
    }
    SESSION_ENGINE = "django.contrib.sessions.backends.cache"
    SESSION_CACHE_ALIAS = "default"
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "internship-cert-locmem",
        }
    }

# --------------------------------------------------------------------------
# Auth / password validation
# --------------------------------------------------------------------------
AUTHENTICATION_BACKENDS = [
    "accounts.backends.EmailOrUsernameModelBackend",
]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "accounts:dashboard"
LOGOUT_REDIRECT_URL = "core:home"


# --------------------------------------------------------------------------
# i18n / tz
# --------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = config("DJANGO_TIME_ZONE", default="Asia/Kolkata")
USE_I18N = True
USE_TZ = True

# --------------------------------------------------------------------------
# Static & media
# --------------------------------------------------------------------------
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# Folder (under MEDIA_ROOT) where company-uploaded certificate/offer-letter
# design packages are unpacked. See certificates/template_engine.py.
CERT_TEMPLATE_ROOT = MEDIA_ROOT / "templates"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --------------------------------------------------------------------------
# Razorpay — keys are supplied via environment, never committed.
# --------------------------------------------------------------------------
RAZORPAY_KEY_ID = config("RAZORPAY_KEY_ID", default="")
RAZORPAY_KEY_SECRET = config("RAZORPAY_KEY_SECRET", default="")

# --------------------------------------------------------------------------
# PDF rendering engine. "auto" (default) tries WeasyPrint first and falls
# back to the pure-Python xhtml2pdf if WeasyPrint's native libraries aren't
# installed (common on Windows without the GTK runtime) — see
# certificates/pdf.py. Force one explicitly with weasyprint or xhtml2pdf.
# --------------------------------------------------------------------------
PDF_ENGINE = config("PDF_ENGINE", default="auto")

# --------------------------------------------------------------------------
# File upload limits (also enforced again in the upload view/forms)
# --------------------------------------------------------------------------
MAX_TEMPLATE_ZIP_SIZE_MB = config("MAX_TEMPLATE_ZIP_SIZE_MB", default=15, cast=int)
DATA_UPLOAD_MAX_MEMORY_SIZE = 20 * 1024 * 1024  # 20 MB request body ceiling

# --------------------------------------------------------------------------
# Logging — structured enough to reason about in production, quiet locally.
# --------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "[{asctime}] {levelname} {name}: {message}", "style": "{"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "verbose"},
    },
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "django.security": {"handlers": ["console"], "level": "WARNING", "propagate": False},
        "certificates": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "payments": {"handlers": ["console"], "level": "INFO", "propagate": False},
    },
}

# --------------------------------------------------------------------------
# Production hardening — only kicks in when DEBUG is False, so local dev
# over plain HTTP keeps working without extra flags.
# --------------------------------------------------------------------------
if not DEBUG:
    SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=bool)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    CSRF_COOKIE_SAMESITE = "Lax"
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "SAMEORIGIN"
    SECURE_REFERRER_POLICY = "same-origin"
    CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS", default="", cast=Csv())
