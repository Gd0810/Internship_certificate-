import logging
import shutil
import uuid
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.forms import StyledAuthenticationForm
from accounts.models import InternProfile
from payments.models import Payment
from certificates.models import CertificateTemplate, OfferLetterTemplate
from certificates.template_engine import extract_template_package, TemplatePackageError, render_template_html
from certificates.rendering import render_offer_letter, render_certificate, _kind_root, _build_context
from certificates.views import _inject_preview_styles
from .decorators import company_staff_required
from .forms import TrackForm, TaskModuleForm, TemplateUploadForm, CategoryForm, CertificateTemplateForm
from .models import InternshipTrack, TaskModule, TrackCategory, UserTaskProgress

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
    form = TrackForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Internship track created.")
        return redirect("company:track_list")
    return render(request, "company/track_form.html", {"form": form, "mode": "Create"})


@company_staff_required
def track_edit(request, pk):
    track = get_object_or_404(InternshipTrack, pk=pk)
    form = TrackForm(request.POST or None, request.FILES or None, instance=track)
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


# -------------------------------------------------------- Track Categories ----
@company_staff_required
def category_list(request):
    categories = TrackCategory.objects.all().order_by("name")
    return render(request, "company/category_list.html", {"categories": categories})


@company_staff_required
def category_create(request):
    form = CategoryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Track category created.")
        return redirect("company:category_list")
    return render(request, "company/category_form.html", {"form": form, "mode": "Create"})


@company_staff_required
def category_edit(request, pk):
    category = get_object_or_404(TrackCategory, pk=pk)
    form = CategoryForm(request.POST or None, instance=category)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Category updated.")
        return redirect("company:category_list")
    return render(request, "company/category_form.html", {"form": form, "mode": "Edit", "category": category})


@company_staff_required
@require_POST
def category_delete(request, pk):
    category = get_object_or_404(TrackCategory, pk=pk)
    category.delete()
    messages.success(request, "Category deleted.")
    return redirect("company:category_list")


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


CERT_DEFAULT_MAP = {
    "default_1": ("default-cfe8f3a2", "Default One (Classic Framed)"),
    "default_2": ("demo-certificate-badge", "Default Two (Modern Ribbon & Badge)"),
}


@company_staff_required
def certificate_template_upload(request):
    if request.method == "POST":
        form = CertificateTemplateForm(request.POST, request.FILES)
        if form.is_valid():
            track = form.cleaned_data["track"]
            choice = form.cleaned_data["template_choice"]
            track_label = track.name if track else "Global (All Tracks)"

            if choice in CERT_DEFAULT_MAP:
                folder_path, name_label = CERT_DEFAULT_MAP[choice]
                # Deactivate previous active templates for this track scope
                CertificateTemplate.objects.filter(track=track).update(is_active=False)

                # Find or create template record
                tpl = CertificateTemplate.objects.filter(track=track, folder_path=folder_path).first()
                if tpl:
                    tpl.is_active = True
                    tpl.save(update_fields=["is_active"])
                else:
                    CertificateTemplate.objects.create(track=track, folder_path=folder_path, is_active=True)

                messages.success(request, f"Certificate template '{name_label}' has been applied to {track_label}.")
                return redirect("company:certificate_template_upload")

            elif choice == "custom":
                package = form.cleaned_data["package"]
                if package.size > settings.MAX_TEMPLATE_ZIP_SIZE_MB * 1024 * 1024:
                    form.add_error("package", f"File exceeds {settings.MAX_TEMPLATE_ZIP_SIZE_MB} MB limit.")
                else:
                    folder_slug = track.slug if track else "default"
                    unique_folder = f"{folder_slug}-{uuid.uuid4().hex[:8]}"
                    destination = Path(settings.CERT_TEMPLATE_ROOT) / "certificate" / unique_folder

                    try:
                        if destination.exists():
                            shutil.rmtree(destination)
                        extract_template_package(package, destination, max_size_mb=settings.MAX_TEMPLATE_ZIP_SIZE_MB)
                        CertificateTemplate.objects.filter(track=track).update(is_active=False)
                        CertificateTemplate.objects.create(track=track, folder_path=unique_folder, is_active=True)
                        messages.success(request, f"Custom certificate design uploaded and activated for {track_label}.")
                        return redirect("company:certificate_template_upload")
                    except TemplatePackageError as exc:
                        shutil.rmtree(destination, ignore_errors=True)
                        form.add_error("package", str(exc))
    else:
        active_global = CertificateTemplate.objects.filter(track__isnull=True, is_active=True).first()
        initial_choice = "default_1"
        if active_global:
            if "demo-certificate-badge" in active_global.folder_path:
                initial_choice = "default_2"
            elif "default-cfe8f3a2" in active_global.folder_path:
                initial_choice = "default_1"
            else:
                initial_choice = "custom"
        form = CertificateTemplateForm(initial={"template_choice": initial_choice})

    templates = CertificateTemplate.objects.select_related("track").order_by("-is_active", "-uploaded_at")[:20]
    return render(request, "company/template_upload.html", {
        "form": form,
        "kind": "Certificate",
        "templates": templates,
        "action_name": "company:certificate_template_upload",
    })


@company_staff_required
def certificate_preset_preview(request, preset_key):
    folder_map = {
        "default_1": "default-cfe8f3a2",
        "default_2": "demo-certificate-badge",
    }
    folder_path = folder_map.get(preset_key, preset_key)
    folder = _kind_root("certificate") / folder_path
    if not (folder / "index.html").exists():
        return HttpResponse("<p style='font-family:sans-serif;padding:40px;color:#8a8a86;'>Certificate template not found.</p>")

    profile = InternProfile.objects.select_related("user", "track").first()
    media_prefix = f"{settings.MEDIA_URL}templates/certificate/{folder_path}/"
    context = _build_context(profile, is_certificate=True, request=request)
    html = render_template_html(folder, context, media_prefix)
    return HttpResponse(_inject_preview_styles(html))


@company_staff_required
@require_POST
def certificate_template_activate(request, pk):
    tpl = get_object_or_404(CertificateTemplate, pk=pk)
    CertificateTemplate.objects.filter(track=tpl.track).update(is_active=False)
    tpl.is_active = True
    tpl.save(update_fields=["is_active"])
    track_name = tpl.track.name if tpl.track else "Global (All Tracks)"
    messages.success(request, f"Template '{tpl.folder_path}' is now active for {track_name}.")
    return redirect("company:certificate_template_upload")


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


# ------------------------------------------------------------- Students ----
@company_staff_required
def student_list(request):
    search_query = request.GET.get("q", "").strip()
    track_filter = request.GET.get("track", "").strip()
    status_filter = request.GET.get("status", "").strip()

    students_qs = InternProfile.objects.select_related("user", "track", "track__category").order_by("-created_at")

    if search_query:
        students_qs = students_qs.filter(
            Q(full_name__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(intern_id__icontains=search_query) |
            Q(college_name__icontains=search_query) |
            Q(mobile_number__icontains=search_query)
        )

    if track_filter:
        students_qs = students_qs.filter(track_id=track_filter)

    if status_filter == "paid":
        students_qs = students_qs.filter(has_paid=True)
    elif status_filter == "unpaid":
        students_qs = students_qs.filter(has_paid=False)

    total_count = students_qs.count()
    paginator = Paginator(students_qs, 15)
    page_obj = paginator.get_page(request.GET.get("page"))

    tracks = InternshipTrack.objects.all().order_by("name")

    stats = {
        "total": InternProfile.objects.count(),
        "paid": InternProfile.objects.filter(has_paid=True).count(),
        "unpaid": InternProfile.objects.filter(has_paid=False).count(),
    }

    return render(
        request,
        "company/student_list.html",
        {
            "page_obj": page_obj,
            "tracks": tracks,
            "search_query": search_query,
            "track_filter": track_filter,
            "status_filter": status_filter,
            "total_count": total_count,
            "stats": stats,
        },
    )


@company_staff_required
def student_detail(request, pk):
    student = get_object_or_404(
        InternProfile.objects.select_related("user", "track", "track__category"),
        pk=pk,
    )

    tasks = list(student.track.task_modules.all().order_by("module_number", "order", "id"))
    progress_map = {
        p.task_id: p for p in UserTaskProgress.objects.filter(profile=student)
    }

    task_rows = []
    for task in tasks:
        prog = progress_map.get(task.id)
        task_rows.append({
            "task": task,
            "progress": prog,
            "is_completed": bool(prog and prog.is_completed),
            "completed_at": prog.completed_at if prog else None,
            "submission_data": prog.submission_data if prog else {},
        })

    payments = student.payments.all().order_by("-created_at")

    return render(
        request,
        "company/student_detail.html",
        {
            "student": student,
            "task_rows": task_rows,
            "payments": payments,
        },
    )


@company_staff_required
@require_POST
def student_toggle_payment(request, pk):
    student = get_object_or_404(InternProfile, pk=pk)
    student.has_paid = not student.has_paid
    if student.has_paid and not student.certificate_id:
        student.generate_certificate_id()
    student.save()
    messages.success(
        request,
        f"Payment status updated for {student.full_name}: {'Verified & Paid' if student.has_paid else 'Pending Payment'}."
    )
    return redirect("company:student_detail", pk=pk)


@company_staff_required
@require_POST
def student_toggle_task(request, pk, task_id):
    student = get_object_or_404(InternProfile, pk=pk)
    task = get_object_or_404(TaskModule, pk=task_id, track=student.track)

    prog, _ = UserTaskProgress.objects.get_or_create(profile=student, task=task)
    prog.is_completed = not prog.is_completed
    if prog.is_completed:
        prog.completed_at = timezone.now()
    else:
        prog.completed_at = None
    prog.save()

    messages.success(
        request,
        f"Module {task.module_number} ('{task.title}') marked as {'Completed' if prog.is_completed else 'Pending'} for {student.full_name}."
    )
    return redirect("company:student_detail", pk=pk)


@company_staff_required
def student_offer_letter_preview(request, pk):
    student = get_object_or_404(InternProfile, pk=pk)
    html = render_offer_letter(student)
    if html is None:
        return HttpResponse("<p style='font-family:sans-serif;padding:40px;color:#8a8a86;'>Offer letter template not configured for this track.</p>")
    return HttpResponse(_inject_preview_styles(html))


@company_staff_required
def student_certificate_preview(request, pk):
    student = get_object_or_404(InternProfile, pk=pk)
    html = render_certificate(student, request=request)
    if html is None:
        return HttpResponse("<p style='font-family:sans-serif;padding:40px;color:#8a8a86;'>Certificate template not configured for this track.</p>")
    return HttpResponse(_inject_preview_styles(html))

