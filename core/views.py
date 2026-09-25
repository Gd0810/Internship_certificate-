from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from company.models import InternshipTrack
from accounts.models import InternProfile


def _lookup_intern_profile(raw_query):
    if not raw_query:
        return None, False, None

    query = raw_query.strip().upper()
    profiles = InternProfile.objects.select_related("track").filter(
        Q(intern_id__iexact=query) | Q(certificate_id__iexact=query)
    )

    if not profiles.exists():
        if query.isdigit():
            formatted_id = f"RBS/INT/{query}"
            profiles = InternProfile.objects.select_related("track").filter(intern_id__iexact=formatted_id)
        elif "RBS/INT/" not in query:
            profiles = InternProfile.objects.select_related("track").filter(intern_id__icontains=query)

    profile = profiles.first()
    error_message = None if profile else f"No intern profile found matching '{raw_query}'."
    return profile, True, error_message


def home(request):
    featured_tracks = (
        InternshipTrack.objects.filter(is_active=True).order_by("-created_at")[:6]
    )
    raw_query = request.GET.get("intern_id", "").strip()
    profile, searched, error_message = _lookup_intern_profile(raw_query)

    return render(
        request,
        "core/home.html",
        {
            "featured_tracks": featured_tracks,
            "query": raw_query,
            "profile": profile,
            "searched": searched,
            "error_message": error_message,
        },
    )


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


def verify(request):
    raw_query = request.GET.get("intern_id", "").strip()
    profile, searched, error_message = _lookup_intern_profile(raw_query)

    if request.headers.get("x-requested-with") == "XMLHttpRequest" or request.GET.get("format") == "json":
        if profile:
            return JsonResponse({
                "success": True,
                "found": True,
                "intern_id": profile.intern_id,
                "full_name": profile.full_name,
                "college_name": profile.college_name or "N/A",
                "degree": profile.degree or "N/A",
                "track_name": profile.track.name if profile.track else "N/A",
                "completed_tasks": profile.completed_tasks,
                "total_tasks": profile.total_tasks,
                "progress_percent": profile.progress_percent,
                "all_tasks_completed": profile.all_tasks_completed,
                "has_paid": profile.has_paid,
                "certificate_id": profile.certificate_id or None,
                "created_at": profile.created_at.strftime("%b %d, %Y"),
            })
        else:
            return JsonResponse({
                "success": True,
                "found": False,
                "error": error_message or f"No record found for '{raw_query}'."
            })

    return render(
        request,
        "core/verify.html",
        {
            "query": raw_query,
            "profile": profile,
            "searched": searched,
            "error_message": error_message,
        },
    )

