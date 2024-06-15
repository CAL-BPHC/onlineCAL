import random

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect, render

from ... import models, permissions
from .portal import BasePortalFilter


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

    faculty: models.Faculty = models.Faculty.objects.get(id=request.user.id)

    return render(
        request,
        "booking_portal/portal_forms/base_portal.html",
        {
            "page_obj": page_obj,
            "filter_form": f.form,
            "user_type": "faculty",
            "user_is_student": False,
            "modifiable_request_status": models.Request.WAITING_FOR_FACULTY,
            "balance": faculty.balance,
            "department": faculty.department,
        },
    )


@login_required
@user_passes_test(permissions.is_faculty)
def faculty_request_accept(request, id):
    if request.method == "POST":
        try:
            with transaction.atomic():
                request_object: models.Request = models.Request.objects.get(
                    id=id, status=models.Request.WAITING_FOR_FACULTY
                )
                needs_department_approval = request.POST.get("departmentRoute", False)
                faculty = request_object.faculty
                if faculty == models.Faculty.objects.get(id=request.user.id):
                    if needs_department_approval:
                        if not faculty.department:
                            messages.error(
                                request,
                                "You need to be assigned to a department to request department approval",
                            )
                            return redirect("faculty_portal")
                        request_object.needs_department_approval = True
                        request_object.status = models.Request.WAITING_FOR_DEPARTMENT
                    else:
                        request_object.status = models.Request.WAITING_FOR_LAB_ASST
                        faculty.balance -= request_object.total_cost
                    request_object.lab_assistant = random.choice(
                        models.LabAssistant.objects.filter(is_active=True)
                    )
                    request_object.save()
                    faculty.save()
                    return redirect("faculty_portal")
                else:
                    return HttpResponse("Bad Request")
        except Exception as e:
            print(e)
            raise Http404("Page Not Found")
    else:
        return HttpResponseBadRequest("Method not allowed")


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
