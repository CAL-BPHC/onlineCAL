import random

from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect

from .portal import BasePortalFilter
from ... import models, permissions


@login_required
@user_passes_test(permissions.is_faculty)
def faculty_portal(request):
    f = BasePortalFilter(
        request.GET,
        queryset=models.Request.objects.filter(faculty=request.user)
        .select_related("slot")
        .order_by("-slot__date"),
    )
    page_obj = f.paginate()

    return render(
        request,
        "booking_portal/portal_forms/base_portal.html",
        {
            "page_obj": page_obj,
            "filter_form": f.form,
            "user_type": "faculty",
            "user_is_student": False,
            "modifiable_request_status": models.Request.WAITING_FOR_FACULTY,
        },
    )


@login_required
@user_passes_test(permissions.is_faculty)
def faculty_request_accept(request, id):
    try:
        with transaction.atomic():
            request_object = models.Request.objects.get(
                id=id, status=models.Request.WAITING_FOR_FACULTY
            )
            faculty = request_object.faculty
            if faculty == models.Faculty.objects.get(id=request.user.id):
                request_object.status = models.Request.WAITING_FOR_LAB_ASST
                request_object.lab_assistant = random.choice(
                    models.LabAssistant.objects.all()
                )
                request_object.save()
                return redirect("faculty_portal")
            else:
                return HttpResponse("Bad Request")
    except Exception:
        raise Http404("Page Not Found")


@login_required
@user_passes_test(permissions.is_faculty)
def faculty_request_reject(request, id):
    try:
        with transaction.atomic():
            request_object = models.Request.objects.get(
                id=id, status=models.Request.WAITING_FOR_FACULTY
            )
            faculty = request_object.faculty
            if faculty == models.Faculty.objects.get(id=request.user.id):
                request_object.status = models.Request.REJECTED
                request_object.save()
                return redirect("faculty_portal")
            else:
                return HttpResponse("Bad Request")
    except Exception:
        raise Http404("Page Not Found")
