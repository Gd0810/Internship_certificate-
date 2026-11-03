import hashlib
import hmac
import json
import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

try:
    import razorpay
except ImportError:  # pragma: no cover
    razorpay = None

from .models import Payment

logger = logging.getLogger("payments")


def _client():
    if not (settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET):
        return None
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


@login_required
@require_POST
def create_order(request):
    """Creates a Razorpay Order for the intern's own track at the effective price (with discount/free support)."""
    profile = getattr(request.user, "intern_profile", None)
    if profile is None:
        return JsonResponse({"ok": False, "error": "No profile."}, status=400)
    if profile.has_paid:
        return JsonResponse({"ok": False, "error": "Already paid."}, status=400)
    if not profile.all_tasks_completed:
        return JsonResponse({"ok": False, "error": "Complete all task modules first."}, status=400)

    # 1. Free track handling: Unlock instantly without calling Razorpay
    if profile.track.is_completely_free:
        import uuid
        from django.utils import timezone

        free_order_ref = f"FREE_{uuid.uuid4().hex[:12].upper()}"
        Payment.objects.create(
            profile=profile,
            track=profile.track,
            razorpay_order_id=free_order_ref,
            razorpay_payment_id="FREE_CLAIM",
            razorpay_signature="FREE_UNLOCKED",
            amount=0,
            status="paid",
            verified_at=timezone.now(),
        )

        profile.has_paid = True
        profile.save(update_fields=["has_paid"])
        profile.generate_certificate_id()

        logger.info("Free certificate unlocked for profile %s on track %s", profile.id, profile.track.slug)
        return JsonResponse({
            "ok": True,
            "is_free": True,
            "certificate_id": profile.certificate_id,
            "message": "Certificate unlocked successfully for free!",
        })

    # 2. Paid track (either regular price or discounted price)
    client = _client()
    charge_amount = profile.track.effective_price
    amount_paise = int(charge_amount * 100)

    if client is None:
        # Razorpay keys not yet configured — surface a clear error rather than
        # silently pretending payment succeeded.
        return JsonResponse(
            {"ok": False, "error": "Payments are not configured yet. Add RAZORPAY_KEY_ID/SECRET."},
            status=503,
        )

    order = client.order.create({
        "amount": amount_paise,
        "currency": "INR",
        "payment_capture": 1,
        "notes": {
            "profile_id": profile.id,
            "track": profile.track.slug,
            "has_discount": profile.track.has_discount,
        },
    })

    Payment.objects.create(
        profile=profile,
        track=profile.track,
        razorpay_order_id=order["id"],
        amount=charge_amount,
        status="created",
    )

    return JsonResponse({
        "ok": True,
        "is_free": False,
        "order_id": order["id"],
        "amount": amount_paise,
        "currency": "INR",
        "key_id": settings.RAZORPAY_KEY_ID,
        "name": "Internship Certificate",
        "profile_name": profile.full_name,
        "email": request.user.email,
        "contact": profile.mobile_number,
    })


@login_required
@require_POST
def verify_payment(request):
    """
    Verifies the Razorpay checkout response server-side before unlocking
    anything. The client-side "success" callback is never trusted alone —
    we always recompute the HMAC signature ourselves.
    """
    profile = getattr(request.user, "intern_profile", None)
    if profile is None:
        return JsonResponse({"ok": False, "error": "No profile."}, status=400)

    try:
        payload = json.loads(request.body.decode("utf-8"))
        order_id = payload["razorpay_order_id"]
        payment_id = payload["razorpay_payment_id"]
        signature = payload["razorpay_signature"]
    except (KeyError, ValueError):
        return JsonResponse({"ok": False, "error": "Malformed payload."}, status=400)

    try:
        payment = Payment.objects.get(razorpay_order_id=order_id, profile=profile, status="created")
    except Payment.DoesNotExist:
        return JsonResponse({"ok": False, "error": "Unknown or already-processed order."}, status=404)

    expected_signature = hmac.new(
        key=settings.RAZORPAY_KEY_SECRET.encode(),
        msg=f"{order_id}|{payment_id}".encode(),
        digestmod=hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(expected_signature, signature):
        payment.status = "failed"
        payment.save(update_fields=["status"])
        logger.warning("Razorpay signature mismatch for order %s", order_id)
        return JsonResponse({"ok": False, "error": "Signature verification failed."}, status=400)

    from django.utils import timezone

    payment.razorpay_payment_id = payment_id
    payment.razorpay_signature = signature
    payment.status = "paid"
    payment.verified_at = timezone.now()
    payment.save()

    profile.has_paid = True
    profile.save(update_fields=["has_paid"])
    profile.generate_certificate_id()

    logger.info("Payment verified for profile %s, order %s", profile.id, order_id)
    return JsonResponse({"ok": True, "certificate_id": profile.certificate_id})
