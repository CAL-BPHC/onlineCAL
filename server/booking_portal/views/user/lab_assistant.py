from typing import cast

from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.http import Http404
from django.shortcuts import redirect, render

from ... import models, permissions
from .portal import BasePortalFilter, get_pagintion_nav_range


@login_required
@user_passes_test(permissions.is_lab_assistant)
def lab_assistant_portal(request):
    f = BasePortalFilter(
        request.GET,
        queryset=models.StudentRequest.objects.order_by("-slot__date", "-pk"),
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
            "modifiable_request_status": models.StudentRequest.WAITING_FOR_LAB_ASST,
        },
    )


@login_required
@user_passes_test(permissions.is_lab_assistant)
def lab_assistant_faculty_portal(request):
    f = BasePortalFilter(
        request.GET,
        queryset=models.FacultyRequest.objects.order_by("-slot__date", "-pk"),
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
            "modifiable_request_status": models.FacultyRequest.WAITING_FOR_LAB_ASST,
            "faculty_request": True,
        },
    )


@login_required
@user_passes_test(permissions.is_lab_assistant)
def lab_assistant_accept(request, id):
    is_faculty = (request.GET.get("is_faculty", False)) == "true"
    try:
        with transaction.atomic():
            if is_faculty:
                request_object = models.FacultyRequest.objects.get(
                    id=id, status=models.FacultyRequest.WAITING_FOR_LAB_ASST
                )
            else:
                request_object = models.StudentRequest.objects.get(
                    id=id, status=models.StudentRequest.WAITING_FOR_LAB_ASST
                )
            if request_object.needs_department_approval:
                department = cast(models.Department, request_object.faculty.department)
                department.balance -= request_object.total_cost
                department.save()
            else:
                faculty = request_object.faculty
                faculty.balance -= request_object.total_cost
                faculty.save()
            request_object.lab_assistant = models.LabAssistant.objects.get(
                id=request.user.id
            )
            request_object.status = models.StudentRequest.APPROVED
            request_object.save()
            return redirect(
                request.META.get(
                    "HTTP_REFERER",
                    "lab_assistant_faculty_portal" if is_faculty else "lab_assistant",
                )
            )
    except Exception:
        raise Http404("Page Not Found")


@transaction.atomic
@login_required
@user_passes_test(permissions.is_lab_assistant)
def lab_assistant_reject(request, id):
    is_faculty = (request.GET.get("is_faculty", False)) == "true"
    try:
        with transaction.atomic():
            if is_faculty:
                request_object = models.FacultyRequest.objects.get(
                    id=id, status=models.FacultyRequest.WAITING_FOR_LAB_ASST
                )
            else:
                request_object: models.StudentRequest = (
                    models.StudentRequest.objects.get(
                        id=id, status=models.StudentRequest.WAITING_FOR_LAB_ASST
                    )
                )
            request_object.status = models.StudentRequest.REJECTED
            request_object.save()
            return redirect(
                request.META.get(
                    "HTTP_REFERER",
                    "lab_assistant_faculty_portal" if is_faculty else "lab_assistant",
                )
            )
    except Exception:
        raise Http404("Page Not Found")
