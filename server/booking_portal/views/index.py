from typing import cast

from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import Http404
from django.shortcuts import render

from ..config import view_application_dict
from ..models import (
    AdditionalPricingRules,
    Department,
    Faculty,
    FacultyRequest,
    LabAssistant,
    Student,
    StudentRequest,
    UserDetail,
)
from ..permissions import get_user_type, is_department, is_faculty, is_lab_assistant


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

    for charge_data in request_obj.additional_charges:
        charge_id = charge_data["id"]
        rule_type = charge_data["rule_type"]

        if (
            rule_type == AdditionalPricingRules.FLAT
            or rule_type == AdditionalPricingRules.PER_SAMPLE
            or rule_type == AdditionalPricingRules.PER_TIME_UNIT
        ):
            data[f"additional_charge_{charge_id}"] = True
        elif rule_type == AdditionalPricingRules.CHOICE_FIELD:
            selected_choice = charge_data.get("selected_choice", "")
            if selected_choice:
                data[f"additional_charge_{charge_id}"] = selected_choice
        elif rule_type == AdditionalPricingRules.CONDITIONAL_FIELD:
            data[f"additional_charge_{charge_id}"] = True
            data[f"conditional_quantity_{charge_id}"] = charge_data.get(
                "conditional_quantity", None
            )
    form_object = form(data)

    # initialize mode
    mode_description = request_obj.mode_description
    mode_cost = request_obj.mode_cost

    if mode_description and mode_cost:
        mode_display = f"{mode_description} - Rs {mode_cost}"
        form_object.fields["mode"].choices = [(-1, mode_display)]
        form_object.fields["mode"].initial = -1

    # initialize field names
    for charge_data in request_obj.additional_charges:
        charge_id = charge_data["id"]
        rule_type = charge_data["rule_type"]

        if rule_type == AdditionalPricingRules.HELP_TEXT:
            continue
        if not rule_type == AdditionalPricingRules.CONDITIONAL_FIELD:
            form_object.fields[
                f"additional_charge_{charge_id}"
            ].label = f"{charge_data['description']} - Rs {charge_data['cost']}"
        else:
            form_object.fields[
                f"additional_charge_{charge_id}"
            ].label = f"{charge_data['description']} - Rs {charge_data['cost']}"
            form_object.fields[f"conditional_quantity_{charge_id}"].label = charge_data[
                "conditional_text"
            ]

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
            or (
                field_val == "department_remarks"
                and get_user_type(request.user) == "department"
            )
        ) and form_field_value is None:
            form_object.fields[field_val].widget.attrs["readonly"] = False

        else:
            form_object.fields[field_val].widget.attrs["disabled"] = True
            form_object.fields[field_val].widget.attrs["readonly"] = True

        if field_val.startswith("conditional_quantity"):
            form_object.fields[field_val].widget.attrs["style"] = ""

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

    for charge_data in request_obj.additional_charges:
        charge_id = charge_data["id"]
        rule_type = charge_data["rule_type"]

        if (
            rule_type == AdditionalPricingRules.FLAT
            or rule_type == AdditionalPricingRules.PER_SAMPLE
            or rule_type == AdditionalPricingRules.PER_TIME_UNIT
        ):
            data[f"additional_charge_{charge_id}"] = True
        elif rule_type == AdditionalPricingRules.CHOICE_FIELD:
            selected_choice = charge_data.get("selected_choice", "")
            if selected_choice:
                data[f"additional_charge_{charge_id}"] = selected_choice
        elif rule_type == AdditionalPricingRules.CONDITIONAL_FIELD:
            data[f"additional_charge_{charge_id}"] = True
            data[f"conditional_quantity_{charge_id}"] = charge_data.get(
                "conditional_quantity", None
            )

    form_object = form(data, is_faculty=True)

    # initialize mode
    mode_description = request_obj.mode_description
    mode_cost = request_obj.mode_cost

    if mode_description and mode_cost:
        mode_display = f"{mode_description} - Rs {mode_cost}"
        form_object.fields["mode"].choices = [(-1, mode_display)]
        form_object.fields["mode"].initial = -1

    # initialize field names
    for charge_data in request_obj.additional_charges:
        charge_id = charge_data["id"]
        rule_type = charge_data["rule_type"]

        if rule_type == AdditionalPricingRules.HELP_TEXT:
            continue
        if not rule_type == AdditionalPricingRules.CONDITIONAL_FIELD:
            form_object.fields[
                f"additional_charge_{charge_id}"
            ].label = f"{charge_data['description']} - Rs {charge_data['cost']}"
        else:
            form_object.fields[
                f"additional_charge_{charge_id}"
            ].label = f"{charge_data['description']} - Rs {charge_data['cost']}"
            form_object.fields[f"conditional_quantity_{charge_id}"].label = charge_data[
                "conditional_text"
            ]

    # Check if Faculty and Assistant remarks are filled once, if yes
    # then these are made read-only
    for field_val, val in form_object.fields.items():
        form_field_value = form_object[field_val].value()
        if (
            (
                field_val == "lab_assistant_remarks"
                and get_user_type(request.user) == "assistant"
            )
            or (
                field_val == "department_remarks"
                and get_user_type(request.user) == "department"
            )
        ) and form_field_value is None:
            form_object.fields[field_val].widget.attrs["readonly"] = False

        else:
            form_object.fields[field_val].widget.attrs["disabled"] = True
            form_object.fields[field_val].widget.attrs["readonly"] = True

        if field_val.startswith("conditional_quantity"):
            form_object.fields[field_val].widget.attrs["style"] = ""
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


@user_passes_test(
    lambda user: is_faculty(user) or is_lab_assistant(user) or is_department(user)
)
@login_required
def add_remarks(request, id):
    """View for saving remarks entered by Faculty/Lab Assistant.
    Remark once added cannot be updated again

    :returns
        HttpResponse object from `show_applicaton` view"""
    is_faculty_request = (request.GET.get("is_faculty", False)) == "true"
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
    elif is_department(request.user):
        content_object.department_remarks = form_fields["department_remarks"]

    content_object.save(
        update_fields=["faculty_remarks", "lab_assistant_remarks", "department_remarks"]
    )
    return show_application(request, id)
