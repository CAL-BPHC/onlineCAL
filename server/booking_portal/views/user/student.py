from typing import cast

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from ... import config, permissions
from ...models import Instrument, Slot, Student, StudentRequest
from .portal import BasePortalFilter


@login_required
@user_passes_test(permissions.is_student)
def student_portal(request):
    f = BasePortalFilter(
        request.GET,
        queryset=StudentRequest.objects.filter(student=request.user)
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
            "user_type": "student",
            "user_is_student": True,
            "modifiable_request_status": "",  # student cannot modify
        },
    )


@login_required
@user_passes_test(permissions.is_student)
def book_machine(request, instr_id):
    """View for booking machine"""

    # Retrieve form/form_model from template_dict
    form_class, form_model_class = config.form_template_dict.get(instr_id, (None, None))
    if not form_class or not form_model_class:
        messages.error(request, "Bad Request")
        return HttpResponseRedirect(reverse("instrument-list"))

    slot_id = request.GET.get("slots", None)
    if not slot_id:
        messages.error(request, "Bad Request")
        return HttpResponseRedirect(reverse("instrument-list"))

    student = Student.objects.select_related("supervisor").get(id=request.user.id)
    supervisor = student.supervisor

    default_context = {
        "edit": True,
        "instrument_title": form_class.title,
        "instrument_subtitle": form_class.subtitle,
        "instrument_verbose_name": form_model_class._meta.verbose_name,
        "form_notes": form_class.help_text,
        "user_type": "student",
        "status": StudentRequest.WAITING_FOR_FACULTY,
    }

    if request.method == "GET":
        slot, instr = cast(
            tuple[Slot, Instrument], Slot.objects.get_instr_from_slot_id(slot_id)
        )
        if not instr or not slot:
            messages.error(request, "Invalid slot or instrument.")
            return HttpResponseRedirect(reverse("instrument-list"))

        if not slot.is_available_for_booking():
            messages.error(request, "Sorry, This slot is not available anymore.")
            return HttpResponseRedirect(reverse("instrument-list"))

        if StudentRequest.objects.has_student_booked_upcoming_instrument_slot(
            instr, student
        ):
            messages.error(
                request, "You already have an ongoing application for this machine."
            )
            return HttpResponseRedirect(reverse("instrument-list"))

        # Render form with initial data
        default_context["cost_per_sample"] = instr.cost_per_sample
        return render(
            request,
            "booking_portal/instrument_form.html",
            {
                "form": form_class(
                    initial={
                        "user_name": student.id,
                        "sup_name": supervisor.id,
                        "sup_dept": supervisor.department,
                        "date": slot.date,
                        "time": slot.start_time,
                        "duration": slot.duration_verbose,
                    }
                ),
                **default_context,
            },
        )
    elif request.method == "POST":
        # Validate and process the form
        form = form_class(request.POST)
        if not form.is_valid():
            return render(
                request,
                "booking_portal/instrument_form.html",
                {"form": form, **default_context},
            )

        try:
            StudentRequest.objects.create_request(form, slot_id, student)
            messages.success(request, "Slot booked successfully.")
            return HttpResponseRedirect(reverse("student"))
        except (ObjectDoesNotExist, ValueError) as e:
            # \\n to escape Javascript
            messages.error(
                request,
                f"Could not proccess your request, please try again. ({str(e)})",
            )
            return HttpResponseRedirect(reverse("instrument-list"))
    else:
        messages.error(request, "Bad Request")
        return HttpResponseRedirect("/")
