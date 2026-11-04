import json
import logging

from django.contrib import messages
from django.contrib.auth import get_user_model, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.db import transaction
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from company.models import InternshipTrack, TaskModule, UserTaskProgress
from .forms import RegistrationForm, StyledAuthenticationForm
from .models import InternProfile

User = get_user_model()
logger = logging.getLogger("accounts")


def register(request):
    # Only redirect to student dashboard if the logged-in user is an enrolled student
    if request.user.is_authenticated and hasattr(request.user, "intern_profile"):
        return redirect("accounts:dashboard")

    track_slug = request.GET.get("track")
    initial_data = {}
    if track_slug:
        selected_track = InternshipTrack.objects.filter(slug=track_slug, is_active=True).first()
        if selected_track:
            initial_data["track"] = selected_track.id

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            with transaction.atomic():
                user = User.objects.create_user(
                    username=data["email"],
                    email=data["email"],
                    password=data["password"],
                    first_name=data["full_name"].split(" ")[0][:30],
                )
                InternProfile.objects.create(
                    user=user,
                    full_name=data["full_name"],
                    college_name=data.get("college_name", "") or "",
                    degree=data.get("degree", "") or "",
                    district=data.get("district", "") or "",
                    track=data["track"],
                    mobile_number=data["mobile_number"],
                )
            auth_login(request, user, backend="accounts.backends.EmailOrUsernameModelBackend")
            logger.info("New intern registered: %s", user.email)
            return redirect("accounts:dashboard")
    else:
        form = RegistrationForm(initial=initial_data)

    return render(request, "accounts/register.html", {"form": form})


class AccountLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = StyledAuthenticationForm
    redirect_authenticated_user = True

    def get_success_url(self):
        if self.request.user.is_staff:
            return reverse("company:overview")
        return super().get_success_url()


class AccountLogoutView(LogoutView):
    next_page = "core:home"


@login_required
def dashboard(request):
    if request.user.is_staff:
        return redirect("company:overview")

    profile = getattr(request.user, "intern_profile", None)
    if profile is None:
        messages.info(request, "You do not have an intern profile associated with this account.")
        return redirect("core:home")

    tab = request.GET.get("tab", "dashboard")
    if tab not in {"dashboard", "offer-letter", "task", "certificate"}:
        tab = "dashboard"

    tasks = list(
        profile.track.task_modules.all().prefetch_related("progress_records")
    )
    progress_map = {
        p.task_id: p for p in UserTaskProgress.objects.filter(profile=profile)
    }
    task_rows = []
    for t in tasks:
        p = progress_map.get(t.id)
        sub_data = p.submission_data if (p and p.submission_data) else {}
        raw_delivs = t.deliverables if isinstance(t.deliverables, list) else []
        clean_delivs = [str(d).strip() for d in raw_delivs if str(d).strip()]

        deliverable_items = []
        missing_count = 0
        for deliv in clean_delivs:
            val = str(sub_data.get(deliv, "")).strip()
            if not val:
                missing_count += 1
            deliverable_items.append({
                "name": deliv,
                "value": val,
                "is_submitted": bool(val),
            })

        has_deliverables = len(clean_delivs) > 0
        all_deliverables_submitted = has_deliverables and (missing_count == 0)

        task_rows.append({
            "task": t,
            "completed": p.is_completed if p else False,
            "submission_data": sub_data,
            "deliverable_items": deliverable_items,
            "has_deliverables": has_deliverables,
            "all_deliverables_submitted": all_deliverables_submitted,
            "missing_count": missing_count,
        })

    from urllib.parse import quote

    track_name = profile.track.name if profile.track else "Internship Program"
    clean_track_tag = "".join(ch for ch in track_name.title() if ch.isalnum())
    track_tag_str = f" #{clean_track_tag}" if clean_track_tag else ""
    offer_share_text = (
        f"Excited to share that I have received an Internship Offer for {track_name} with Redback IT Solutions Private Limited! 💼🚀\n\n"
        f"Looking forward to learning, building real-world projects, and gaining hands-on industry experience.\n\n"
        f"#InternshipOffer #OfferLetter #Redback #CareerGrowth #Learning #Internship{track_tag_str}"
    )
    linkedin_offer_share_text = offer_share_text
    linkedin_offer_share_url = f"https://www.linkedin.com/feed/?shareActive=true&text={quote(offer_share_text)}"

    linkedin_share_url = ""
    linkedin_share_text = ""
    linkedin_add_cert_url = ""
    verify_url = ""
    if profile.has_paid:
        try:
            from certificates.qr import get_verification_url
            verify_url = get_verification_url(profile, request=request)
            share_text = (
                f"This is my internship certificate I completed in {track_name} with Redback IT Solutions Private Limited! 🎓🚀\n\n"
                f"#Internship #Certificate #Redback #Learning #CareerGrowth"
            )
            linkedin_share_text = share_text
            linkedin_share_url = f"https://www.linkedin.com/feed/?shareActive=true&text={quote(share_text)}"
        except Exception:
            pass

    context = {
        "profile": profile,
        "active_tab": tab,
        "task_rows": task_rows,
        "linkedin_share_url": linkedin_share_url,
        "linkedin_share_text": linkedin_share_text,
        "linkedin_offer_share_url": linkedin_offer_share_url,
        "linkedin_offer_share_text": linkedin_offer_share_text,
        "verify_url": verify_url,
    }
    return render(request, "accounts/dashboard.html", context)


@login_required
@require_POST
def toggle_task(request, task_id):
    profile = getattr(request.user, "intern_profile", None)
    if profile is None:
        return HttpResponseBadRequest("No profile.")

    try:
        task = TaskModule.objects.get(id=task_id, track=profile.track)
    except TaskModule.DoesNotExist:
        return HttpResponseBadRequest("Invalid task.")

    progress, _ = UserTaskProgress.objects.get_or_create(profile=profile, task=task)

    # If currently not completed, intern is attempting to mark as completed
    if not progress.is_completed:
        raw_delivs = task.deliverables if isinstance(task.deliverables, list) else []
        required_delivs = [str(d).strip() for d in raw_delivs if str(d).strip()]
        if required_delivs:
            curr_data = progress.submission_data or {}
            missing = [d for d in required_delivs if not str(curr_data.get(d, "")).strip()]
            if missing:
                return JsonResponse({
                    "ok": False,
                    "error": f"Please submit links for all required deliverables ({', '.join(missing)}) before marking this module as complete.",
                    "missing": missing,
                }, status=400)
        progress.is_completed = True
        progress.completed_at = timezone.now()
    else:
        progress.is_completed = False
        progress.completed_at = None

    progress.save()

    return JsonResponse({
        "ok": True,
        "task_id": task.id,
        "is_completed": progress.is_completed,
        "completed_count": profile.completed_tasks,
        "total_count": profile.total_tasks,
        "all_completed": profile.all_tasks_completed,
    })


@login_required
@require_POST
def save_submission(request, task_id):
    profile = getattr(request.user, "intern_profile", None)
    if profile is None:
        return HttpResponseBadRequest("No profile.")

    try:
        task = TaskModule.objects.get(id=task_id, track=profile.track)
    except TaskModule.DoesNotExist:
        return HttpResponseBadRequest("Invalid task.")

    try:
        body = json.loads(request.body.decode("utf-8"))
    except Exception:
        body = request.POST

    deliverables_submitted = body.get("deliverables", {})
    mark_complete = body.get("mark_complete", None)

    progress, _ = UserTaskProgress.objects.get_or_create(profile=profile, task=task)
    if deliverables_submitted and isinstance(deliverables_submitted, dict):
        current_sub = progress.submission_data or {}
        for k, v in deliverables_submitted.items():
            if str(k).strip():
                current_sub[str(k).strip()] = str(v).strip()
        progress.submission_data = current_sub

    raw_delivs = task.deliverables if isinstance(task.deliverables, list) else []
    required_delivs = [str(d).strip() for d in raw_delivs if str(d).strip()]

    if mark_complete is not None:
        target_complete = bool(mark_complete)
        if target_complete:
            if required_delivs:
                curr_data = progress.submission_data or {}
                missing = [d for d in required_delivs if not str(curr_data.get(d, "")).strip()]
                if missing:
                    return JsonResponse({
                        "ok": False,
                        "error": f"Please submit links for all required deliverables ({', '.join(missing)}) before marking this module as complete.",
                        "missing": missing,
                        "submission_data": progress.submission_data,
                    }, status=400)
            progress.is_completed = True
            progress.completed_at = timezone.now()
        else:
            progress.is_completed = False
            progress.completed_at = None

    progress.save()

    curr_data = progress.submission_data or {}
    deliverable_items = []
    missing_count = 0
    for d in required_delivs:
        val = str(curr_data.get(d, "")).strip()
        if not val:
            missing_count += 1
        deliverable_items.append({
            "name": d,
            "value": val,
            "is_submitted": bool(val),
        })

    return JsonResponse({
        "ok": True,
        "task_id": task.id,
        "is_completed": progress.is_completed,
        "submission_data": progress.submission_data,
        "deliverable_items": deliverable_items,
        "has_deliverables": len(required_delivs) > 0,
        "all_deliverables_submitted": (len(required_delivs) > 0 and missing_count == 0),
        "completed_count": profile.completed_tasks,
        "total_count": profile.total_tasks,
        "all_completed": profile.all_tasks_completed,
    })
