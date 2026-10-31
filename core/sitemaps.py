from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from company.models import InternshipTrack


class StaticViewSitemap(Sitemap):
    """Sitemap for key static public landing pages."""
    priority = 0.9
    changefreq = "weekly"

    def items(self):
        return [
            ("core:home", 1.0, "daily"),
            ("core:track_list", 0.9, "daily"),
            ("core:about", 0.7, "monthly"),
            ("core:verify", 0.8, "daily"),
        ]

    def location(self, item):
        return reverse(item[0])

    def priority(self, item):
        return item[1]

    def changefreq(self, item):
        return item[2]


class TrackSitemap(Sitemap):
    """Sitemap for all active internship tracks."""
    priority = 0.85
    changefreq = "weekly"

    def items(self):
        return InternshipTrack.objects.filter(is_active=True).order_by("-updated_at")

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()

