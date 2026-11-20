import logging
from typing import cast

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from ... import models, permissions
from ...forms.portal import InstrumentAccessForm, StudentSearchForm
from .portal import BasePortalFilter, get_pagintion_nav_range, portal_return_url

logger = logging.getLogger(__name__)

STUDENTS_PER_PAGE = 25


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
@require_POST
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
                portal_return_url(
                    request,
                    "lab_assistant_faculty_portal" if is_faculty else "lab_assistant",
                )
            )
    except ObjectDoesNotExist:
        raise Http404("Page Not Found")
    except Exception:
        logger.exception("Lab assistant could not accept request %s", id)
        raise Http404("Page Not Found")


@transaction.atomic
@login_required
@user_passes_test(permissions.is_lab_assistant)
@require_POST
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
                portal_return_url(
                    request,
                    "lab_assistant_faculty_portal" if is_faculty else "lab_assistant",
                )
            )
    except ObjectDoesNotExist:
        raise Http404("Page Not Found")
    except Exception:
        logger.exception("Lab assistant could not reject request %s", id)
        raise Http404("Page Not Found")


@login_required
@user_passes_test(permissions.is_lab_assistant)
@require_GET
def lab_assistant_instrument_access(request):
    """Every active student and what they may book, to find whose to change."""
    form = StudentSearchForm(request.GET)
    students = (
        models.Student.objects.filter(is_active=True)
        .select_related("supervisor")
        .prefetch_related("instruments")
        .order_by("name", "pk")
    )
    if form.is_valid():
        query = form.cleaned_data["q"]
        if query:
            students = students.filter(
                Q(name__icontains=query) | Q(email__icontains=query)
            )
        if form.cleaned_data["instrument"]:
            students = students.filter(instruments=form.cleaned_data["instrument"])

    return render(
        request,
        "booking_portal/portal_forms/instrument_access.html",
        {
            "form": form,
            "page_obj": Paginator(students, STUDENTS_PER_PAGE).get_page(
                request.GET.get("page")
            ),
            "user_type": "assistant",
        },
    )


@login_required
@user_passes_test(permissions.is_lab_assistant)
def lab_assistant_student_instruments(request, student_id):
    """Assign a student an instrument once they are trained on it, or revoke it."""
    student = get_object_or_404(
        models.Student.objects.select_related("supervisor"), pk=student_id
    )
    if request.method == "POST":
        form = InstrumentAccessForm(request.POST)
        if form.is_valid():
            instrument = form.cleaned_data["instrument"]
            # one instrument at a time, so lab assistants changing the same
            # student at once do not undo each other
            if form.cleaned_data["action"] == InstrumentAccessForm.ASSIGN:
                student.instruments.add(instrument)
                messages.success(request, f"{student.name} can now book {instrument}.")
            else:
                student.instruments.remove(instrument)
                messages.success(
                    request, f"{student.name} can no longer book {instrument}."
                )
        else:
            messages.error(request, "Choose an instrument first.")
        return redirect(request.get_full_path())

    return render(
        request,
        "booking_portal/portal_forms/student_instruments.html",
        {
            "student": student,
            "assigned": student.instruments.all(),
            "unassigned": models.Instrument.objects.exclude(students=student),
            "user_type": "assistant",
        },
    )
