from django.shortcuts import render, redirect
from django.http import HttpResponseNotAllowed
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.signing import BadSignature, SignatureExpired
from django.conf import settings
from .services import RegistrationService
from .models import Registration
from notifications.services import send_notification
from .qr import make_checkin_token, make_qr_png_base64, signer


def _redirect_back(request, fallback_url: str):
    next_url = request.POST.get('next') or request.GET.get('next')
    if next_url:
        return redirect(next_url)
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect(fallback_url)


@login_required
def register_activity(request, activity_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    fallback = reverse('ngo:activity_detail', kwargs={'activity_id': activity_id})
    try:
        reg = RegistrationService.register_user(request.user, activity_id)
        messages.success(request, "Registration successful.")
        send_notification(request.user, f'You registered for "{reg.activity.title}".')
    except ValueError as e:
        msg = str(e)
        if 'already registered' in msg.lower():
            messages.info(request, msg)
        else:
            messages.error(request, msg)

    return _redirect_back(request, fallback)


@login_required
def my_registrations(request):
    registrations = (
        Registration.objects.filter(employee=request.user, status='active')
        .select_related('activity')
        .order_by('-registered_at')
    )
    return render(request, 'registration/my_registrations.html', {'registrations': registrations})


@login_required
def qr_checkin(request):
    """
    Employee-facing QR page.
    Shows a QR code for a selected active registration (activity).
    """
    activity_id = request.GET.get("activity_id")
    registration = None
    qr_png_b64 = None
    token = None

    if activity_id:
        try:
            registration = Registration.objects.select_related("activity").get(
                employee=request.user, activity_id=activity_id, status="active"
            )
        except Registration.DoesNotExist:
            registration = None

    if registration:
        token = make_checkin_token(registration.id, request.user.id, registration.activity_id)
        relative = reverse("registration:checkin_token", kwargs={"token": token})
        base = getattr(settings, "PUBLIC_BASE_URL", "") or ""
        if base:
            checkin_url = base.rstrip("/") + relative
        else:
            checkin_url = request.build_absolute_uri(relative)
        qr_png_b64 = make_qr_png_base64(checkin_url)

    my_regs = (
        Registration.objects.filter(employee=request.user, status="active")
        .select_related("activity")
        .order_by("-registered_at")
    )

    return render(
        request,
        "registration/qr_checkin.html",
        {
            "my_regs": my_regs,
            "selected_registration": registration,
            "qr_png_b64": qr_png_b64,
            "checkin_token": token,
            "checkin_url": checkin_url if registration else None,
        },
    )


@login_required
def checkin_token(request, token: str):
    """
    Admin-facing check-in endpoint. This is what the QR encodes.
    """
    if not request.user.is_admin():
        messages.error(request, "Only admin can perform check-in.")
        return redirect("ngo:activity_list")

    try:
        unsigned = signer.unsign(token, max_age=60 * 60 * 24 * 2)  # 48h
        reg_id, employee_id, activity_id = [int(x) for x in unsigned.split(":")]
    except SignatureExpired:
        messages.error(request, "QR token expired.")
        return redirect("ngo:activity_list")
    except (BadSignature, ValueError):
        messages.error(request, "Invalid QR token.")
        return redirect("ngo:activity_list")

    try:
        reg = Registration.objects.select_related("employee", "activity").get(
            id=reg_id, employee_id=employee_id, activity_id=activity_id
        )
    except Registration.DoesNotExist:
        messages.error(request, "Registration not found.")
        return redirect("ngo:activity_list")

    if reg.status != "active":
        messages.error(request, "Registration is not active.")
        return redirect("ngo:activity_detail", activity_id=reg.activity_id)

    if reg.checked_in_at:
        messages.info(request, "Already checked in.")
        return redirect("ngo:activity_detail", activity_id=reg.activity_id)

    reg.checked_in_at = timezone.now()
    reg.checked_in_by = request.user
    reg.save(update_fields=["checked_in_at", "checked_in_by"])
    send_notification(reg.employee, f'Attendance recorded for "{reg.activity.title}".')
    messages.success(request, f'Checked in {reg.employee.username} for "{reg.activity.title}".')
    return redirect("ngo:activity_detail", activity_id=reg.activity_id)


@login_required
def cancel_activity(request, activity_id):
    """Cancel the logged-in user's registration for an activity.

    Expects POST. Marks the Registration.status as 'cancelled' if it exists
    and is currently active.
    """
    if request.method != 'POST':
        return HttpResponseNotAllowed(["POST"])

    try:
        reg = Registration.objects.get(employee=request.user, activity_id=activity_id)
    except Registration.DoesNotExist:
        messages.error(request, 'Registration not found.')
        fallback = reverse('ngo:activity_detail', kwargs={'activity_id': activity_id})
        return _redirect_back(request, fallback)

    if reg.status != 'active':
        messages.info(request, 'Registration already cancelled.')
        fallback = reverse('ngo:activity_detail', kwargs={'activity_id': activity_id})
        return _redirect_back(request, fallback)

    reg.status = 'cancelled'
    reg.save()
    messages.success(request, 'Registration cancelled.')
    send_notification(request.user, f'You cancelled your registration for "{reg.activity.title}".')
    fallback = reverse('ngo:activity_detail', kwargs={'activity_id': activity_id})
    return _redirect_back(request, fallback)