from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render

from ..config import form_template_dict
from ..forms.portal import InstrumentList
from ..models import Faculty, Instrument, Slot, Student, StudentRequest
from ..permissions import is_student


@login_required
@user_passes_test(is_student)
def instrument_list(request):
    form = InstrumentList()
    return render(
        request, "booking_portal/portal_forms/instrument_list.html", {"form": form}
    )
