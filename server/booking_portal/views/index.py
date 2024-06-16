from typing import cast

from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import Http404
from django.shortcuts import render

from ..config import view_application_dict
from ..models import (
    Department,
    Faculty,
    FacultyRequest,
    LabAssistant,
    Student,
    StudentRequest,
    UserDetail,
)
from ..permissions import get_user_type, is_faculty, is_lab_assistant


def index(request):
    """Returns homepage for users"""
    context = {}
    faculty_instance = Faculty.objects.filter(id=request.user.id).first()
    student_instance = Student.objects.filter(id=request.user.id).first()
    lab_instance = LabAssistant.objects.filter(id=request.user.id).first()
    department_instance = Department.objects.filter(id=request.user.id).first()

    if faculty_instance:
        context = "faculty"
    elif student_instance:
        context = "student"
    elif lab_instance:
        context = "assistant"
    elif department_instance:
        context = "department"
    else:
        context = "none"

    return render(request, "home.html", {"user_type": context})


def show_application_student(request, id):
    try:
        request_obj: StudentRequest = StudentRequest.objects.get(id=id)
    except Exception:
        raise Http404()
    content_object = cast(UserDetail, request_obj.content_object)
    form = view_application_dict[content_object._meta.model]

    data = content_object.__dict__
    data["user_name"] = Student.objects.get(id=data["user_id"])
    data["sup_name"] = Faculty.objects.get(id=data["sup_name_id"])
    form_object = form(data)

    # Check if Faculty and Assistant remarks are filled once, if yes
    # then these are made read-only
    for field_val, val in form_object.fields.items():
        form_field_value = form_object[field_val].value()
        if (
            (
                field_val == "faculty_remarks"
                and get_user_type(request.user) == "faculty"
            )
            or (
                field_val == "lab_assistant_remarks"
                and get_user_type(request.user) == "assistant"
            )
        ) and form_field_value is None:
            form_object.fields[field_val].widget.attrs["readonly"] = False

        else:
            form_object.fields[field_val].widget.attrs["disabled"] = True
            form_object.fields[field_val].widget.attrs["readonly"] = True

    return render(
        request,
        "booking_portal/instrument_form.html",
        {
            "form": form_object,
            "edit": False,
            "user_type": get_user_type(request.user),
            "id": id,
            "instrument_title": form.title,
            "instrument_subtitle": form.subtitle,
            "instrument_verbose_name": content_object._meta.verbose_name,
            "form_notes": form.help_text,
            "status": request_obj.status,
            "cost_per_sample": request_obj.slot.instrument.cost_per_sample,
            "total_cost": request_obj.total_cost,
        },
    )


def show_application_faculty(request, id):
    is_faculty = Faculty.objects.filter(id=request.user.id).exists()
    try:
        request_obj: FacultyRequest = FacultyRequest.objects.get(id=id)
    except Exception:
        raise Http404()
    content_object = cast(UserDetail, request_obj.content_object)
    form = view_application_dict[content_object._meta.model]

    data = content_object.__dict__
    data["user_name"] = Faculty.objects.get(id=data["user_id"])
    data["needs_department_approval"] = request_obj.needs_department_approval

    form_object = form(data, is_faculty=True)

    # Check if Faculty and Assistant remarks are filled once, if yes
    # then these are made read-only
    for field_val, val in form_object.fields.items():
        form_field_value = form_object[field_val].value()
        if (
            field_val == "lab_assistant_remarks"
            and get_user_type(request.user) == "assistant"
        ) and form_field_value is None:
            form_object.fields[field_val].widget.attrs["readonly"] = False

        else:
            form_object.fields[field_val].widget.attrs["disabled"] = True
            form_object.fields[field_val].widget.attrs["readonly"] = True

    return render(
        request,
        "booking_portal/instrument_form.html",
        {
            "form": form_object,
            "edit": False,
            "user_type": "student" if is_faculty else get_user_type(request.user),
            "id": id,
            "instrument_title": form.title,
            "instrument_subtitle": form.subtitle,
            "instrument_verbose_name": content_object._meta.verbose_name,
            "form_notes": form.help_text,
            "status": request_obj.status,
            "cost_per_sample": request_obj.slot.instrument.cost_per_sample,
            "total_cost": request_obj.total_cost,
            "faculty_request": True,
        },
    )


@login_required
def show_application(request, id):
    """Displays application details of a user.
    Can be accessed from the Requests Page"""
    is_faculty = (request.GET.get("is_faculty", False)) == "true"
    if is_faculty:
        return show_application_faculty(request, id)

    return show_application_student(request, id)


@user_passes_test(lambda user: is_faculty(user) or is_lab_assistant(user))
@login_required
def add_remarks(request, id):
    """View for saving remarks entered by Faculty/Lab Assistant.
    Remark once added cannot be updated again

    :returns
        HttpResponse object from `show_applicaton` view"""
    is_faculty_request = (request.GET.get("is_faculty", False)) == "true"
    print(is_faculty_request)
    try:
        if is_faculty_request:
            request_obj = FacultyRequest.objects.get(id=id)
        else:
            request_obj = StudentRequest.objects.get(id=id)
    except Exception:
        raise Http404()
    content_object = request_obj.content_object
    form_fields = dict(request.POST.items())

    if is_faculty(request.user):
        content_object.faculty_remarks = form_fields["faculty_remarks"]
    elif is_lab_assistant(request.user):
        content_object.lab_assistant_remarks = form_fields["lab_assistant_remarks"]

    content_object.save(update_fields=["faculty_remarks", "lab_assistant_remarks"])
    return show_application(request, id)
