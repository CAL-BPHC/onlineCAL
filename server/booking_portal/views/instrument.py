from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render

from ..config import form_template_dict
from ..forms.portal import InstrumentList
from ..models import Faculty, Instrument, Request, Slot, Student
from ..permissions import is_student, is_faculty


@login_required
@user_passes_test(lambda user: is_student(user) or is_faculty(user))
def instrument_list(request):
    form = InstrumentList()
    return render(request, 'booking_portal/portal_forms/instrument_list.html', {'form': form})
