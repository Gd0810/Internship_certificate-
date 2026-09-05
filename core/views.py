from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from company.models import InternshipTrack


def home(request):
    featured_tracks = (
        InternshipTrack.objects.filter(is_active=True).order_by("-created_at")[:6]
    )
    return render(request, "core/home.html", {"featured_tracks": featured_tracks})


def track_list(request):
    tracks_qs = InternshipTrack.objects.filter(is_active=True).order_by("name")
    paginator = Paginator(tracks_qs, 9)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "core/track_list.html", {"page_obj": page_obj})


def track_detail(request, slug):
    track = get_object_or_404(InternshipTrack, slug=slug, is_active=True)
    module_count = track.task_modules.count()
    return render(
        request, "core/track_detail.html", {"track": track, "module_count": module_count}
    )


def about(request):
    return render(request, "core/about.html")
