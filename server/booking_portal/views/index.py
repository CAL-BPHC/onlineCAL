from django.http import Http404
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test

from ..models import Faculty, Student, LabAssistant, Request
from ..config import view_application_dict
from ..permissions import get_user_type, is_faculty, is_lab_assistant


def index(request):
    """Returns homepage for users"""
    context = {}
    faculty_instance = Faculty.objects.filter(id=request.user.id).first()
    student_instance = Student.objects.filter(id=request.user.id).first()
    lab_instance = LabAssistant.objects.filter(id=request.user.id).first()
    if faculty_instance:
        context = "faculty"
    elif student_instance:
        context = "student"
    elif lab_instance:
        context = "assistant"
    else:
        context = "none"

    return render(request, "home.html", {"user_type": context})


@login_required
def show_application(request, id):
    """Displays application details of a user.
    Can be accessed from the Requests Page"""
    try:
        request_obj = Request.objects.get(id=id)
    except Exception:
        raise Http404()
    content_object = request_obj.content_object
    form = view_application_dict[content_object._meta.model]

    data = content_object.__dict__
    data["user_name"] = Student.objects.get(id=data["user_name_id"])
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
        },
    )


@user_passes_test(lambda user: is_faculty(user) or is_lab_assistant(user))
@login_required
def add_remarks(request, id):
    """View for saving remarks entered by Faculty/Lab Assistant.
    Remark once added cannot be updated again

    :returns
        HttpResponse object from `show_applicaton` view"""
    try:
        request_obj = Request.objects.get(id=id)
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
