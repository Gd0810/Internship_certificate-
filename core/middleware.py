"""
Lightweight login-attempt throttling.

This guards the two most sensitive POST endpoints (user login and the
hidden company login) against brute-force attempts without adding a
hard dependency on an external package. It keys on client IP + path in
the cache backend configured in settings (LocMemCache locally, Redis in
production), so it scales correctly across multiple app servers once
Redis is configured.
"""
from django.core.cache import cache
from django.http import HttpResponse

THROTTLED_PATH_PREFIXES = ("/accounts/login", "/accounts/register")
MAX_ATTEMPTS = 10
WINDOW_SECONDS = 300


def _client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")


class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == "POST" and request.path.startswith(THROTTLED_PATH_PREFIXES):
            key = f"ratelimit:{_client_ip(request)}:{request.path}"
            attempts = cache.get(key, 0)
            if attempts >= MAX_ATTEMPTS:
                return HttpResponse(
                    "Too many attempts. Please wait a few minutes and try again.",
                    status=429,
                )
            cache.set(key, attempts + 1, timeout=WINDOW_SECONDS)
        return self.get_response(request)
