from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render

from ..forms.portal import InstrumentList
from ..permissions import is_faculty, is_student


@login_required
@user_passes_test(lambda u: is_student(u) or is_faculty(u))
def instrument_list(request):
    form = InstrumentList()
    return render(
        request, "booking_portal/portal_forms/instrument_list.html", {"form": form}
    )
