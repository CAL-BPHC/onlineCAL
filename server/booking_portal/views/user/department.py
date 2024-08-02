from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.db.models import BooleanField, Value
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render

from ... import models, permissions
from .portal import BasePortalFilter, get_pagintion_nav_range


@login_required
@user_passes_test(permissions.is_department)
def department_portal(request):
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

    combined_requests = faculty_requests.union(student_requests)
    combined_requests = combined_requests.order_by("-slot__date", "pk")

    f = BasePortalFilter(
        request.GET,
        queryset=(combined_requests),
    )
    page_obj = f.paginate()
    department = models.Department.objects.get(id=request.user.id)

    return render(
        request,
        "booking_portal/portal_forms/base_portal.html",
        {
            "page_obj": page_obj,
            "nav_range": get_pagintion_nav_range(page_obj),
            "filter_form": f.form,
            "user_type": "department",
            "user_is_student": False,
            "balance": department.balance,
            "modifiable_request_status": models.StudentRequest.WAITING_FOR_DEPARTMENT,
        },
    )


@login_required
@user_passes_test(permissions.is_department)
def department_accept(request, id):
    is_faculty = (request.GET.get("is_faculty", False)) == "true"
    try:
        with transaction.atomic():
            if is_faculty:
                request_object = models.FacultyRequest.objects.get(
                    id=id, status=models.FacultyRequest.WAITING_FOR_DEPARTMENT
                )
            else:
                request_object: models.StudentRequest = (
                    models.StudentRequest.objects.get(
                        id=id, status=models.StudentRequest.WAITING_FOR_DEPARTMENT
                    )
                )
            department = models.Department.objects.get(id=request.user.id)
            if department == request_object.faculty.department:
                request_object.status = models.StudentRequest.WAITING_FOR_LAB_ASST
                request_object.save()
                return redirect("department_portal")
            else:
                return HttpResponse("Bad Request")
    except Exception as e:
        print(e)
        raise Http404("Page Not Found")


@login_required
@user_passes_test(permissions.is_department)
def department_reject(request, id):
    is_faculty = (request.GET.get("is_faculty", False)) == "true"
    try:
        with transaction.atomic():
            if is_faculty:
                request_object = models.FacultyRequest.objects.get(
                    id=id, status=models.FacultyRequest.WAITING_FOR_DEPARTMENT
                )
            else:
                request_object = models.StudentRequest.objects.get(
                    id=id, status=models.StudentRequest.WAITING_FOR_DEPARTMENT
                )
            department = request_object.faculty.department
            if department == models.Department.objects.get(id=request.user.id):
                request_object.status = models.StudentRequest.REJECTED
                request_object.save()
                return redirect("department_portal")
            else:
                return HttpResponse("Bad Request")
    except Exception:
        raise Http404("Page Not Found")
        raise Http404("Page Not Found")
