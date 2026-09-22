from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import BooleanField, Value
from django.shortcuts import render
from django.views.decorators.http import require_GET

from ... import models, permissions, reporting
from .portal import (
    BasePortalFilter,
    active_filter_scope,
    get_pagintion_nav_range,
    usage_summary,
)


@login_required
@user_passes_test(permissions.is_department)
def department_portal(request):
    """Every request billed to the department, read-only.

    The department's approval is taken as given, so there is nothing here to
    accept or reject: the list is a ledger of what its faculty booked.
    """
    student_requests = (
        models.StudentRequest.objects.filter(
            faculty__department=request.user,
            needs_department_approval=True,
        )
        .select_related("slot")
        .annotate(is_faculty_request=Value(False, output_field=BooleanField()))
    )
    faculty_requests = (
        models.FacultyRequest.objects.filter(
            faculty__department=request.user,
            needs_department_approval=True,
        )
        .select_related("slot")
        .annotate(is_faculty_request=Value(True, output_field=BooleanField()))
    )
    f = BasePortalFilter(
        request.GET,
        student_queryset=student_requests,
        faculty_queryset=faculty_requests,
    )
    page_obj = f.paginate()

    return render(
        request,
        "booking_portal/portal_forms/base_portal.html",
        {
            "page_obj": page_obj,
            "nav_range": get_pagintion_nav_range(page_obj),
            "filter_form": f.form,
            "filter_scope": active_filter_scope(f),
            "user_type": "department",
            "user_is_student": False,
        },
    )


@login_required
@user_passes_test(permissions.is_department)
@require_GET
def department_usage_summary(request):
    """Faculty and instrument wise usage billed to the logged in department."""
    return usage_summary(request, reporting.collect_department_usage, request.user)
