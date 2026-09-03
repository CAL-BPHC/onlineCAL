import datetime
from typing import cast

from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ValidationError
from django.db.models import Model
from django.forms import ModelChoiceField
from django.http import Http404
from django.shortcuts import render
from django.urls import reverse

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
from .user.portal import safe_portal_url


# The remark fields are read as a group at the end of an application rather
# than inline with the sample details.
REMARK_FIELDS = (
    ("student_remarks", "Applicant"),
    ("faculty_remarks", "Supervisor"),
    ("department_remarks", "Department HoD"),
    ("lab_assistant_remarks", "Lab assistant"),
)


# The slot line in the summary header already states these.
SLOT_FIELDS = ("date", "time", "duration")
SUPERVISOR_FIELDS = ("sup_name", "sup_dept")


def _display_value(bound_field):
    """What a submitted answer should read as, rather than what it was typed into."""
    value = bound_field.value()
    field = bound_field.field

    if isinstance(field, ModelChoiceField):
        if value in (None, ""):
            return ""
        if isinstance(value, Model):
            return field.label_from_instance(value)
        try:
            # the stored value is a primary key; show it the way the form did
            return field.label_from_instance(field.to_python(value))
        except (ValidationError, AttributeError):
            return str(value)
    if isinstance(value, bool):
        return "Yes" if value else "No"
    # spell dates and times out rather than leaving them to locale formatting,
    # which renders 12:00 as "noon"
    if isinstance(value, datetime.datetime):
        return value.strftime("%d %b %Y, %I:%M %p")
    if isinstance(value, datetime.date):
        return value.strftime("%d %b %Y")
    if isinstance(value, datetime.time):
        return value.strftime("%I:%M %p").lstrip("0")

    choices = list(getattr(field, "choices", None) or [])
    if choices:
        labels = {str(key): label for key, label in choices}
        if str(value) in labels:
            return labels[str(value)]
        # a mode is pinned to the single option the booking was made with
        if len(choices) == 1:
            return choices[0][1]
    return "" if value is None else value


def _application_rows(form_object, editable_field=None, hidden_fields=()):
    """Split a submitted application into readable detail and remark rows."""
    remark_labels = dict(REMARK_FIELDS)
    details, remarks = [], []

    for bound_field in form_object:
        if bound_field.name == editable_field or bound_field.name in hidden_fields:
            continue
        row = {
            "label": remark_labels.get(bound_field.name) or bound_field.label,
            "value": _display_value(bound_field),
        }
        if bound_field.name in remark_labels:
            # a remark nobody wrote is not worth a row
            if row["value"]:
                remarks.append(row)
        else:
            details.append(row)
    return details, remarks


# Who may act on a request, in which state, and where that lands them. A
# reviewer decides from the application itself so that it has at least been in
# front of them; the department and the lab assistant keep their list buttons
# as well, since they clear far more requests in a sitting.
DECISIONS = {
    "faculty": {
        "status": StudentRequest.WAITING_FOR_FACULTY,
        "accept": "faculty_request_accept",
        "reject": "faculty_request_reject",
        "portal": "faculty_portal",
    },
    "department": {
        "status": StudentRequest.WAITING_FOR_DEPARTMENT,
        "accept": "department_request_accept",
        "reject": "department_request_reject",
        "portal": "department_portal",
    },
    "assistant": {
        "status": StudentRequest.WAITING_FOR_LAB_ASST,
        "accept": "lab_assistant_request_accept",
        "reject": "lab_assistant_request_reject",
        "portal": "lab_assistant",
    },
}


def _owns_the_decision(user, user_type, request_obj):
    """Whether this request is actually this reviewer's to act on."""
    if user_type == "faculty":
        return request_obj.faculty_id == user.id
    if user_type == "department":
        return request_obj.faculty.department_id == user.id
    # lab assistants work the whole queue, as their portal already shows
    return user_type == "assistant"


def _decision(request, user_type, request_obj, faculty_request=False):
    """The accept/reject controls this reviewer gets here, or None."""
    rule = DECISIONS.get(user_type)
    if (
        rule is None
        or request_obj.status != rule["status"]
        or not _owns_the_decision(request.user, user_type, request_obj)
    ):
        return None

    portal = rule["portal"]
    query = ""
    if faculty_request:
        query = "?is_faculty=true"
        if user_type == "assistant":
            portal = "lab_assistant_faculty_portal"
    return {
        "accept_url": reverse(rule["accept"], args=[request_obj.id]) + query,
        "reject_url": reverse(rule["reject"], args=[request_obj.id]) + query,
        "back_url": safe_portal_url(request.META.get("HTTP_REFERER"), request, portal),
    }


def _decision_context(request, user_type, request_obj, decision):
    """What the confirmation modal has to state before this reviewer accepts."""
    empty = {"balance": None, "department": None, "payer": None}
    if decision is None:
        return empty

    if user_type == "faculty":
        faculty = Faculty.objects.filter(id=request.user.id).first()
        if faculty is None:
            return empty
        return {**empty, "balance": faculty.balance, "department": faculty.department}
    if user_type == "department":
        department = Department.objects.filter(id=request.user.id).first()
        return {**empty, "balance": department.balance if department else None}
    # the lab assistant's approval is what actually spends: the bill lands on
    # whoever the request was routed through
    return {
        **empty,
        "payer": request_obj.faculty.department
        if request_obj.needs_department_approval
        else request_obj.faculty,
    }


def _editable_remark_field(user_type):
    return {
        "faculty": "faculty_remarks",
        "assistant": "lab_assistant_remarks",
        "department": "department_remarks",
    }.get(user_type)


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
        elif rule_type == AdditionalPricingRules.CHOICE_FIELD:
            form_object.fields[f"additional_charge_{charge_id}"].label = charge_data[
                "description"
            ]
        elif not rule_type == AdditionalPricingRules.CONDITIONAL_FIELD:
            form_object.fields[
                f"additional_charge_{charge_id}"
            ].label = f"{charge_data['description']} - Rs {charge_data['cost']}"
        else:
            form_object.fields[
                f"additional_charge_{charge_id}"
            ].label = f"{charge_data['description']} - Rs {charge_data['conditional_cost']} per unit"
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

    user_type = get_user_type(request.user)
    remark_field = _editable_remark_field(user_type)
    if remark_field and form_object[remark_field].value() is not None:
        remark_field = None
    hidden = set(SLOT_FIELDS)
    if is_faculty(request.user) and request_obj.faculty_id == request.user.id:
        hidden.update(SUPERVISOR_FIELDS)
    elif user_type == "department" and request_obj.faculty.department_id == (
        request.user.id
    ):
        # the department reading its own requests already knows whose it is
        hidden.add("sup_dept")
    details, remarks = _application_rows(form_object, remark_field, hidden)

    decision = _decision(request, user_type, request_obj)

    return render(
        request,
        "booking_portal/instrument_form.html",
        {
            "form": form_object,
            "edit": False,
            "user_type": user_type,
            "id": id,
            "instrument_title": form.title,
            "instrument_subtitle": form.subtitle,
            "instrument_verbose_name": content_object._meta.verbose_name,
            "form_notes": form.help_text,
            "status": request_obj.status,
            "total_cost": request_obj.total_cost,
            "notes_first": content_object._meta.verbose_name == "ICP-MS",
            "details": details,
            "remarks": remarks,
            "remark_bound_field": form_object[remark_field] if remark_field else None,
            "request_obj": request_obj,
            "decision": decision,
            **_decision_context(request, user_type, request_obj, decision),
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
        elif rule_type == AdditionalPricingRules.CHOICE_FIELD:
            form_object.fields[f"additional_charge_{charge_id}"].label = charge_data[
                "description"
            ]
        elif not rule_type == AdditionalPricingRules.CONDITIONAL_FIELD:
            form_object.fields[
                f"additional_charge_{charge_id}"
            ].label = f"{charge_data['description']} - Rs {charge_data['cost']}"
        else:
            form_object.fields[
                f"additional_charge_{charge_id}"
            ].label = f"{charge_data['description']} - Rs {charge_data['conditional_cost']} per unit"
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
    user_type = "student" if is_faculty else get_user_type(request.user)
    remark_field = _editable_remark_field(user_type)
    if remark_field and form_object[remark_field].value() is not None:
        remark_field = None
    details, remarks = _application_rows(form_object, remark_field, SLOT_FIELDS)

    decision = _decision(request, user_type, request_obj, faculty_request=True)

    return render(
        request,
        "booking_portal/instrument_form.html",
        {
            "form": form_object,
            "edit": False,
            "user_type": user_type,
            "id": id,
            "instrument_title": form.title,
            "instrument_subtitle": form.subtitle,
            "instrument_verbose_name": content_object._meta.verbose_name,
            "form_notes": form.help_text,
            "status": request_obj.status,
            "total_cost": request_obj.total_cost,
            "faculty_request": True,
            "notes_first": content_object._meta.verbose_name == "ICP-MS",
            "details": details,
            "remarks": remarks,
            "remark_bound_field": form_object[remark_field] if remark_field else None,
            "request_obj": request_obj,
            "decision": decision,
            **_decision_context(request, user_type, request_obj, decision),
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
