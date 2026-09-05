import logging
import shutil
import uuid
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from accounts.forms import StyledAuthenticationForm
from accounts.models import InternProfile
from payments.models import Payment
from certificates.models import CertificateTemplate, OfferLetterTemplate
from certificates.template_engine import extract_template_package, TemplatePackageError
from .decorators import company_staff_required
from .forms import TrackForm, TaskModuleForm, TemplateUploadForm
from .models import InternshipTrack, TaskModule

logger = logging.getLogger("company")


def company_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("company:overview")

    form = StyledAuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        if not user.is_staff:
            form.add_error(None, "This account does not have company access.")
        else:
            auth_login(request, user)
            next_url = request.GET.get("next") or "company:overview"
            return redirect(next_url)

    return render(request, "company/login.html", {"form": form})


@company_staff_required
def company_logout(request):
    auth_logout(request)
    return redirect("company:login")


@company_staff_required
def overview(request):
    stats = {
        "tracks": InternshipTrack.objects.count(),
        "interns": InternProfile.objects.count(),
        "paid": InternProfile.objects.filter(has_paid=True).count(),
        "revenue": sum(p.amount for p in Payment.objects.filter(status="paid")),
    }
    recent_interns = InternProfile.objects.select_related("user", "track").order_by("-created_at")[:10]
    return render(request, "company/overview.html", {"stats": stats, "recent_interns": recent_interns})


# ---------------------------------------------------------------- Tracks ----
@company_staff_required
def track_list(request):
    tracks = InternshipTrack.objects.all().order_by("name")
    return render(request, "company/track_list.html", {"tracks": tracks})


@company_staff_required
def track_create(request):
    form = TrackForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Internship track created.")
        return redirect("company:track_list")
    return render(request, "company/track_form.html", {"form": form, "mode": "Create"})


@company_staff_required
def track_edit(request, pk):
    track = get_object_or_404(InternshipTrack, pk=pk)
    form = TrackForm(request.POST or None, instance=track)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Track updated.")
        return redirect("company:track_list")
    return render(request, "company/track_form.html", {"form": form, "mode": "Edit", "track": track})


@company_staff_required
@require_POST
def track_delete(request, pk):
    track = get_object_or_404(InternshipTrack, pk=pk)
    track.delete()
    messages.success(request, "Track deleted.")
    return redirect("company:track_list")


# ----------------------------------------------------------- Task modules ----
@company_staff_required
def task_list(request, track_pk):
    track = get_object_or_404(InternshipTrack, pk=track_pk)
    tasks = track.task_modules.all()
    return render(request, "company/task_list.html", {"track": track, "tasks": tasks})


@company_staff_required
def task_create(request, track_pk):
    track = get_object_or_404(InternshipTrack, pk=track_pk)
    form = TaskModuleForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        task = form.save(commit=False)
        task.track = track
        task.save()
        messages.success(request, "Task module added.")
        return redirect("company:task_list", track_pk=track.pk)
    return render(request, "company/task_form.html", {"form": form, "track": track, "mode": "Add"})


@company_staff_required
def task_edit(request, track_pk, pk):
    track = get_object_or_404(InternshipTrack, pk=track_pk)
    task = get_object_or_404(TaskModule, pk=pk, track=track)
    form = TaskModuleForm(request.POST or None, instance=task)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Task module updated.")
        return redirect("company:task_list", track_pk=track.pk)
    return render(request, "company/task_form.html", {"form": form, "track": track, "mode": "Edit"})


@company_staff_required
@require_POST
def task_delete(request, track_pk, pk):
    task = get_object_or_404(TaskModule, pk=pk, track_id=track_pk)
    task.delete()
    messages.success(request, "Task module deleted.")
    return redirect("company:task_list", track_pk=track_pk)


# ---------------------------------------------------------- Template upload --
def _handle_template_upload(request, model, kind):
    form = TemplateUploadForm(request.POST, request.FILES)
    if not form.is_valid():
        return form, None

    track = form.cleaned_data["track"]
    package = form.cleaned_data["package"]

    if package.size > settings.MAX_TEMPLATE_ZIP_SIZE_MB * 1024 * 1024:
        form.add_error("package", f"File exceeds {settings.MAX_TEMPLATE_ZIP_SIZE_MB} MB limit.")
        return form, None

    folder_slug = track.slug if track else "default"
    unique_folder = f"{folder_slug}-{uuid.uuid4().hex[:8]}"
    destination = Path(settings.CERT_TEMPLATE_ROOT) / kind / unique_folder

    try:
        if destination.exists():
            shutil.rmtree(destination)
        extract_template_package(package, destination, max_size_mb=settings.MAX_TEMPLATE_ZIP_SIZE_MB)
    except TemplatePackageError as exc:
        shutil.rmtree(destination, ignore_errors=True)
        form.add_error("package", str(exc))
        return form, None

    # Deactivate any previous template for the same track/default slot, then
    # record the new one — old files are left on disk for audit/rollback.
    model.objects.filter(track=track).update(is_active=False)
    model.objects.create(track=track, folder_path=unique_folder, is_active=True)
    return form, unique_folder


@company_staff_required
def certificate_template_upload(request):
    unique_folder = None
    if request.method == "POST":
        form, unique_folder = _handle_template_upload(request, CertificateTemplate, "certificate")
        if unique_folder:
            messages.success(request, "Certificate design uploaded and activated.")
            return redirect("company:certificate_template_upload")
    else:
        form = TemplateUploadForm()

    templates = CertificateTemplate.objects.select_related("track").order_by("-uploaded_at")[:20]
    return render(request, "company/template_upload.html", {
        "form": form, "kind": "Certificate", "templates": templates,
        "action_name": "company:certificate_template_upload",
    })


@company_staff_required
def offer_letter_template_upload(request):
    unique_folder = None
    if request.method == "POST":
        form, unique_folder = _handle_template_upload(request, OfferLetterTemplate, "offer_letter")
        if unique_folder:
            messages.success(request, "Offer letter design uploaded and activated.")
            return redirect("company:offer_letter_template_upload")
    else:
        form = TemplateUploadForm()

    templates = OfferLetterTemplate.objects.select_related("track").order_by("-uploaded_at")[:20]
    return render(request, "company/template_upload.html", {
        "form": form, "kind": "Offer Letter", "templates": templates,
        "action_name": "company:offer_letter_template_upload",
    })
