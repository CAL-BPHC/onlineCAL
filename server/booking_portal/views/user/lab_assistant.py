from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.http import Http404
from django.shortcuts import render, redirect

from .portal import BasePortalFilter, get_pagintion_nav_range
from ... import models, permissions


@login_required
@user_passes_test(permissions.is_lab_assistant)
def lab_assistant_portal(request):
    f = BasePortalFilter(
        request.GET, queryset=models.Request.objects.order_by("-slot__date", "-pk")
    )
    page_obj = f.paginate()

    return render(
        request,
        "booking_portal/portal_forms/base_portal.html",
        {
            "page_obj": page_obj,
            "nav_range": get_pagintion_nav_range(page_obj),
            "filter_form": f.form,
            "user_type": "assistant",
            "user_is_student": False,
            "modifiable_request_status": models.Request.WAITING_FOR_LAB_ASST,
        },
    )


@login_required
@user_passes_test(permissions.is_lab_assistant)
def lab_assistant_accept(request, id):
    try:
        with transaction.atomic():
            request_object = models.Request.objects.get(
                id=id, status=models.Request.WAITING_FOR_LAB_ASST
            )
            request_object.lab_assistant = models.LabAssistant.objects.get(
                id=request.user.id
            )
            request_object.status = models.Request.APPROVED
            request_object.save()
            return redirect("lab_assistant")
    except Exception:
        raise Http404("Page Not Found")


@transaction.atomic
@login_required
@user_passes_test(permissions.is_lab_assistant)
def lab_assistant_reject(request, id):
    request_object = models.Request.objects.get(
        id=id, status=models.Request.WAITING_FOR_LAB_ASST
    )
    request_object.lab_assistant = models.LabAssistant.objects.get(id=request.user.id)
    request_object.status = models.Request.REJECTED
    request_object.save()
    return redirect("lab_assistant")
