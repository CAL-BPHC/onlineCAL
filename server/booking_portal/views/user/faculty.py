import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_GET, require_POST

from ... import models, permissions, reporting
from .portal import (
    BasePortalFilter,
    active_filter_scope,
    get_pagintion_nav_range,
    safe_portal_url,
)

logger = logging.getLogger(__name__)


def _portal_context(request, queryset, **extra):
    """Shared context for the two faculty portal pages."""
    portal_filter = BasePortalFilter(request.GET, queryset=queryset)
    page_obj = portal_filter.paginate()
    faculty: models.Faculty = models.Faculty.objects.get(id=request.user.id)

    context = {
        "page_obj": page_obj,
        "nav_range": get_pagintion_nav_range(page_obj),
        "filter_form": portal_filter.form,
        "filter_scope": active_filter_scope(portal_filter),
        "user_type": "faculty",
        "user_is_student": False,
        "balance": faculty.balance,
        "department": faculty.department,
    }
    context.update(extra)
    return context


@login_required
@user_passes_test(permissions.is_faculty)
def faculty_portal(request):
    return render(
        request,
        "booking_portal/portal_forms/base_portal.html",
        _portal_context(
            request,
            models.StudentRequest.objects.filter(faculty=request.user)
            .select_related("slot")
            .order_by("-slot__date"),
            modifiable_request_status=models.StudentRequest.WAITING_FOR_FACULTY,
        ),
    )


@login_required
@user_passes_test(permissions.is_faculty)
def faculty_request_portal(request):
    return render(
        request,
        "booking_portal/portal_forms/base_portal.html",
        _portal_context(
            request,
            models.FacultyRequest.objects.filter(faculty=request.user)
            .select_related("slot")
            .order_by("-slot__date"),
            modifiable_request_status=None,
            faculty_request=True,
        ),
    )


@login_required
@user_passes_test(permissions.is_faculty)
@require_GET
def faculty_usage_summary(request):
    """Instrument and student wise usage for the logged in faculty."""
    preset = request.GET.get("preset") or reporting.DEFAULT_PRESET
    if preset not in reporting.PRESETS:
        return JsonResponse({"error": "Unknown preset"}, status=400)

    start = parse_date(request.GET.get("from") or "")
    end = parse_date(request.GET.get("to") or "")
    if preset == "custom" and not (start or end):
        return JsonResponse(
            {"error": "A custom range needs a valid from or to date"}, status=400
        )

    # The panel can follow the instrument picked in the portal's own filter.
    instrument = None
    instrument_id = request.GET.get("instrument") or ""
    if instrument_id:
        instrument = models.Instrument.objects.filter(pk=instrument_id).first()
        if instrument is None:
            return JsonResponse({"error": "Unknown instrument"}, status=400)

    status = request.GET.get("status") or ""
    if status and status not in dict(models.StudentRequest.STATUS_CHOICES):
        return JsonResponse({"error": "Unknown status"}, status=400)

    start, end, label = reporting.resolve_range(preset, start, end)
    payload = reporting.collect_usage(
        request.user,
        start,
        end,
        instrument.pk if instrument else None,
        status or None,
    )
    payload["range"] = {
        "preset": preset,
        "from": start.isoformat() if start else None,
        "to": end.isoformat() if end else None,
        "label": label,
        "instrument": instrument.name if instrument else None,
    }
    return JsonResponse(payload)


@login_required
@user_passes_test(permissions.is_faculty)
@require_POST
def faculty_request_accept(request, id):
    try:
        with transaction.atomic():
            request_object: models.StudentRequest = models.StudentRequest.objects.get(
                id=id, status=models.StudentRequest.WAITING_FOR_FACULTY
            )
            needs_department_approval = request.POST.get("departmentRoute", False)
            faculty = request_object.faculty
            if faculty != models.Faculty.objects.get(id=request.user.id):
                return HttpResponse("Bad Request")

            if needs_department_approval:
                if not faculty.department:
                    error = (
                        "You need to be assigned to a department to request "
                        "department approval"
                    )
                    messages.error(request, error)
                    return redirect("instrument-list")
                request_object.needs_department_approval = True
                request_object.status = models.StudentRequest.WAITING_FOR_DEPARTMENT
            else:
                request_object.status = models.StudentRequest.WAITING_FOR_LAB_ASST
            request_object.save()

            return redirect(safe_portal_url(request.POST.get("next"), request))
    except models.StudentRequest.DoesNotExist:
        raise Http404("Page Not Found")
    except Exception:
        logger.exception("Failed to accept student request %s", id)
        raise Http404("Page Not Found")


@login_required
@user_passes_test(permissions.is_faculty)
@require_POST
def faculty_request_reject(request, id):
    try:
        with transaction.atomic():
            request_object = models.StudentRequest.objects.get(
                id=id, status=models.StudentRequest.WAITING_FOR_FACULTY
            )
            faculty = request_object.faculty
            if faculty != models.Faculty.objects.get(id=request.user.id):
                return HttpResponse("Bad Request")

            request_object.status = models.StudentRequest.REJECTED
            request_object.save()

            return redirect(safe_portal_url(request.POST.get("next"), request))
    except models.StudentRequest.DoesNotExist:
        raise Http404("Page Not Found")
    except Exception:
        logger.exception("Failed to reject student request %s", id)
        raise Http404("Page Not Found")
