from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from ..forms.portal import InstrumentList, SlotList
from ..models import StudentRequest
from ..permissions import is_faculty, is_student


@login_required
@user_passes_test(lambda u: is_student(u) or is_faculty(u))
def slot_list(request):
    if not request.method == "POST":
        messages.error(request, "Bad Request")
        return HttpResponseRedirect(reverse("instrument-list"))

    form = InstrumentList(request.POST)
    if not form.is_valid():
        messages.error(request, "Bad Request")
        return HttpResponseRedirect(reverse("instrument-list"))

    instr = form.cleaned_data["instruments"]
    if not instr.status:
        # Instrument not available
        messages.error(
            request, "Instrument unavailable due to technica/maintenance reasons."
        )
        return render(
            request,
            "booking_portal/portal_forms/instrument_list.html",
            {
                "form": InstrumentList(),
            },
        )
    if StudentRequest.objects.does_student_have_three_pending_requests(
        instr, request.user
    ):
        messages.error(
            request, "You already have 3 pending requests for this instrument."
        )
        return render(
            request,
            "booking_portal/portal_forms/instrument_list.html",
            {
                "form": InstrumentList(),
            },
        )

    return render(
        request,
        "booking_portal/portal_forms/slot_list.html",
        {
            "instrument_name": instr.name,
            "instrument_id": instr.pk,
            "form": SlotList(instr),
        },
    )
