from typing import cast

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from ... import config, permissions
from ...models import (
    AdditionalPricingRules,
    Faculty,
    FacultyRequest,
    Instrument,
    ModePricingRules,
    Slot,
    Student,
    StudentRequest,
)
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


def book_machine_student(request, form_class, form_model_class):
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
        "notes_first": form_model_class._meta.verbose_name == "ICP-MS",
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

        if StudentRequest.objects.does_student_have_three_pending_requests(
            instr, student
        ):
            messages.error(
                request, "You already have 3 ongoing applications for this machine."
            )
            return HttpResponseRedirect(reverse("instrument-list"))

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
        action = request.POST.get("action")
        if action == "submit":
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
        elif action == "calculate":
            total_cost = 0

            cleaned_data = form.cleaned_data

            slot = Slot.objects.get(id=slot_id)
            duration = slot.duration
            duration_in_minutes = duration.total_seconds() / 60

            # base cost
            mode_id = cleaned_data.get("mode")
            if mode_id:
                mode = ModePricingRules.objects.get(id=mode_id)

                if mode.rule_type == ModePricingRules.FLAT:
                    if mode.cost:
                        total_cost += mode.cost
                elif mode.rule_type == ModePricingRules.PER_SAMPLE:
                    num_samples = cleaned_data.get("number_of_samples")
                    if num_samples and mode.cost:
                        total_cost += mode.cost * num_samples
                elif mode.rule_type == ModePricingRules.PER_TIME_UNIT:
                    if duration and mode.cost:
                        total_cost += mode.cost * (
                            duration_in_minutes / mode.time_in_minutes
                        )

            # additional costs
            for key, value in cleaned_data.items():
                if key.startswith("additional_charge_"):
                    charge_id = key.split("_")[-1]
                    rule = AdditionalPricingRules.objects.get(id=charge_id)

                    if (
                        isinstance(value, str)
                        and rule.rule_type == AdditionalPricingRules.CHOICE_FIELD
                    ):
                        if value and rule.choices:
                            num_samples = cleaned_data.get("number_of_samples")
                            for choice in rule.choices:  # type: ignore
                                if choice["value"] == value:
                                    total_cost += choice["cost"] * num_samples
                    elif value:
                        if rule.rule_type == AdditionalPricingRules.CONDITIONAL_FIELD:
                            quantity = cleaned_data.get(
                                f"conditional_quantity_{charge_id}"
                            )
                            if rule.conditional_cost and quantity:
                                total_cost += rule.conditional_cost * quantity
                        elif rule.rule_type == AdditionalPricingRules.FLAT:
                            if rule.cost:
                                total_cost += rule.cost
                        elif rule.rule_type == AdditionalPricingRules.PER_SAMPLE:
                            num_samples = cleaned_data.get("number_of_samples")
                            if num_samples and rule.cost:
                                total_cost += rule.cost * num_samples
                        elif rule.rule_type == AdditionalPricingRules.PER_TIME_UNIT:
                            if duration and rule.cost:
                                total_cost += rule.cost * (
                                    duration_in_minutes / rule.time_in_minutes
                                )
                        else:
                            if rule.cost:
                                total_cost += rule.cost

            return render(
                request,
                "booking_portal/instrument_form.html",
                {
                    "form": form,
                    **default_context,
                    "calculation_done": True,
                    "total_cost": total_cost,
                },
            )
        else:
            messages.error(request, "Bad Request")
            return HttpResponseRedirect(reverse("instrument-list"))
    else:
        messages.error(request, "Bad Request")
        return HttpResponseRedirect("/")


@login_required
@user_passes_test(lambda u: permissions.is_student(u) or permissions.is_faculty(u))
def book_machine(request, instr_id):
    """View for booking machine"""

    is_student = permissions.is_student(request.user)
    # Retrieve form/form_model from template_dict
    form_class, form_model_class = config.form_template_dict.get(instr_id, (None, None))
    if not form_class or not form_model_class:
        messages.error(request, "Bad Request")
        return HttpResponseRedirect(reverse("instrument-list"))

    if is_student:
        return book_machine_student(request, form_class, form_model_class)

    slot_id = request.GET.get("slots", None)
    if not slot_id:
        messages.error(request, "Bad Request")
        return HttpResponseRedirect(reverse("instrument-list"))

    faculty = Faculty.objects.get(id=request.user.id)

    default_context = {
        "edit": True,
        "instrument_title": form_class.title,
        "instrument_subtitle": form_class.subtitle,
        "instrument_verbose_name": form_model_class._meta.verbose_name,
        "form_notes": form_class.help_text,
        "user_type": "student",
        "status": StudentRequest.WAITING_FOR_FACULTY,  # does not matter when edit is true
        "notes_first": form_model_class._meta.verbose_name == "ICP-MS",
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

        if FacultyRequest.objects.has_faculty_booked_upcoming_instrument_slot(
            instr, faculty
        ):
            messages.error(
                request, "You already have an ongoing application for this machine."
            )
            return HttpResponseRedirect(reverse("instrument-list"))

        return render(
            request,
            "booking_portal/instrument_form.html",
            {
                "form": form_class(
                    initial={
                        "user_name": faculty.id,
                        "date": slot.date,
                        "time": slot.start_time,
                        "duration": slot.duration_verbose,
                    },
                    is_faculty=not is_student,
                ),
                **default_context,
            },
        )
    elif request.method == "POST":
        # Validate and process the form
        form = form_class(request.POST, is_faculty=not is_student)
        if not form.is_valid():
            return render(
                request,
                "booking_portal/instrument_form.html",
                {"form": form(is_faculty=not is_student), **default_context},
            )
        action = request.POST.get("action")
        if action == "submit":
            try:
                FacultyRequest.objects.create_request(form, slot_id, faculty)
                messages.success(request, "Slot booked successfully.")
                return HttpResponseRedirect(reverse("faculty_request_portal"))
            except (ObjectDoesNotExist, ValueError) as e:
                # \\n to escape Javascript
                messages.error(
                    request,
                    f"Could not process your request, please try again. ({str(e)})",
                )
                return HttpResponseRedirect(reverse("instrument-list"))
        elif action == "calculate":
            total_cost = 0

            cleaned_data = form.cleaned_data

            slot = Slot.objects.get(id=slot_id)
            duration = slot.duration
            duration_in_minutes = duration.total_seconds() / 60

            # base cost
            mode_id = cleaned_data.get("mode")
            if mode_id:
                mode = ModePricingRules.objects.get(id=mode_id)

                if mode.rule_type == ModePricingRules.FLAT:
                    if mode.cost:
                        total_cost += mode.cost
                elif mode.rule_type == ModePricingRules.PER_SAMPLE:
                    num_samples = cleaned_data.get("number_of_samples")
                    if num_samples and mode.cost:
                        total_cost += mode.cost * num_samples
                elif mode.rule_type == ModePricingRules.PER_TIME_UNIT:
                    if duration and mode.cost:
                        total_cost += mode.cost * (
                            duration_in_minutes / mode.time_in_minutes
                        )

            # additional costs
            for key, value in cleaned_data.items():
                if key.startswith("additional_charge_"):
                    charge_id = key.split("_")[-1]
                    rule = AdditionalPricingRules.objects.get(id=charge_id)

                    if (
                        isinstance(value, str)
                        and rule.rule_type == AdditionalPricingRules.CHOICE_FIELD
                    ):
                        if value and rule.choices:
                            num_samples = cleaned_data.get("number_of_samples")
                            for choice in rule.choices:  # type: ignore
                                if choice["value"] == value:
                                    total_cost += choice["cost"] * num_samples
                    elif value:
                        if rule.rule_type == AdditionalPricingRules.CONDITIONAL_FIELD:
                            quantity = cleaned_data.get(
                                f"conditional_quantity_{charge_id}"
                            )
                            if rule.conditional_cost and quantity:
                                total_cost += rule.conditional_cost * quantity
                        elif rule.rule_type == AdditionalPricingRules.FLAT:
                            if rule.cost:
                                total_cost += rule.cost
                        elif rule.rule_type == AdditionalPricingRules.PER_SAMPLE:
                            num_samples = cleaned_data.get("number_of_samples")
                            if num_samples and rule.cost:
                                total_cost += rule.cost * num_samples
                        elif rule.rule_type == AdditionalPricingRules.PER_TIME_UNIT:
                            if duration and rule.cost:
                                total_cost += rule.cost * (
                                    duration_in_minutes / rule.time_in_minutes
                                )
                        else:
                            if rule.cost:
                                total_cost += rule.cost

            return render(
                request,
                "booking_portal/instrument_form.html",
                {
                    "form": form,
                    **default_context,
                    "calculation_done": True,
                    "total_cost": total_cost,
                },
            )
        else:
            messages.error(request, "Bad Request")
            return HttpResponseRedirect(reverse("instrument-list"))

    else:
        messages.error(request, "Bad Request")
        return HttpResponseRedirect("/")
