import json
import logging

from django.contrib.auth import get_user_model, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.db import transaction
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.http import require_POST

from company.models import TaskModule, UserTaskProgress
from .forms import RegistrationForm, StyledAuthenticationForm
from .models import InternProfile

User = get_user_model()
logger = logging.getLogger("accounts")


def register(request):
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")

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
                    college_name=data["college_name"],
                    degree=data["degree"],
                    track=data["track"],
                    mobile_number=data["mobile_number"],
                )
            auth_login(request, user, backend="accounts.backends.EmailOrUsernameModelBackend")
            logger.info("New intern registered: %s", user.email)
            return redirect("accounts:dashboard")
    else:
        form = RegistrationForm()

    return render(request, "accounts/register.html", {"form": form})


class AccountLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = StyledAuthenticationForm
    redirect_authenticated_user = True


class AccountLogoutView(LogoutView):
    next_page = "core:home"


@login_required
def dashboard(request):
    profile = getattr(request.user, "intern_profile", None)
    if profile is None:
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
        deliverable_items = []
        for deliv in t.deliverables:
            deliverable_items.append({
                "name": deliv,
                "value": sub_data.get(deliv, "")
            })
        task_rows.append({
            "task": t,
            "completed": p.is_completed if p else False,
            "submission_data": sub_data,
            "deliverable_items": deliverable_items,
        })

    context = {
        "profile": profile,
        "active_tab": tab,
        "task_rows": task_rows,
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
    progress.is_completed = not progress.is_completed
    progress.completed_at = timezone.now() if progress.is_completed else None
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
    if deliverables_submitted:
        current_sub = progress.submission_data or {}
        current_sub.update(deliverables_submitted)
        progress.submission_data = current_sub

    if mark_complete is not None:
        progress.is_completed = bool(mark_complete)
        progress.completed_at = timezone.now() if progress.is_completed else None

    progress.save()

    return JsonResponse({
        "ok": True,
        "task_id": task.id,
        "is_completed": progress.is_completed,
        "submission_data": progress.submission_data,
        "completed_count": profile.completed_tasks,
        "total_count": profile.total_tasks,
        "all_completed": profile.all_tasks_completed,
    })
