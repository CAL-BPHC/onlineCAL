import datetime

from django.contrib import admin, messages
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render
from django.urls import path
from django.utils.translation import gettext_lazy
from rangefilter.filter import DateRangeFilter

from .. import permissions
from ..forms.admin import BulkCreateSlotsForm
from ..models import Instrument, Slot


class SlotFilterByInstrument(admin.SimpleListFilter):
    # Name to be displayed on the admin portal
    title = gettext_lazy("Instrument")

    parameter_name = 'instrument'

    def lookups(self, request, model_admin):
        """Returns a list of tuples. The first element
        in each tuple is the coded value for the option
        that will appear in the URL query. The second value
        is the human-readable name for the option that will
        appear in the right side bar"""

        return (
            (instr.id, gettext_lazy(str(instr)))
            for instr in Instrument.objects.all()
        )

    def queryset(self, request, queryset):
        """Returns the filtered queryset based on the
        value provided in the query string and retrievable
        via `self.value()`"""

        return (
            queryset if self.value() is None
            else queryset.filter(instrument__id=self.value())
        )


class SlotAdmin(admin.ModelAdmin):
    change_list_template = "admin/slot_change_list.html"
    list_filter = (
        ('date', DateRangeFilter),
        'status',
        SlotFilterByInstrument
    )
    list_display = admin.ModelAdmin.list_display + ('status',)

    # 'Add Slot' button is only visible to the admin
    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        return False

    @staticmethod
    def time_left(current, end, duration):
        """Checks if a slot can be made with `current time` and
        `duration` before the `end time`"""
        today = datetime.date.today()
        diff = (datetime.datetime.combine(today, end) -
                datetime.datetime.combine(today, current))

        return diff >= duration

    def get_urls(self):
        urls = super().get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name

        my_urls = [
            path("bulk-slots/", SlotAdmin.generate_slots,
                 name='%s_%s_bulk-slots_create' % info)
        ]
        return my_urls + urls

    @staticmethod
    def render_bulk_slots_form(request, form):
        payload = {
            "form": form,
            "opts": Slot._meta,
            "has_view_permission": True,
        }
        return render(request, "admin/bulk_import_slots_form.html", payload)

    @staticmethod
    @user_passes_test(lambda u: permissions.is_lab_assistant(u) or u.is_superuser)
    def generate_slots(request):
        """Bulk Import Slots has a form for creating slots.
        This form is restricted to staff.
        """
        if request.method == 'POST':
            form = BulkCreateSlotsForm(request.POST)
            if not form.is_valid():
                return SlotAdmin.render_bulk_slots_form(request, form)

            instr = form.cleaned_data['instrument']
            start_date = form.cleaned_data['start_date']
            start_time = form.cleaned_data['start_time']
            end_time = form.cleaned_data['end_time']
            duration = form.cleaned_data['slot_duration']
            day_count = int(form.cleaned_data['for_the_next'])

            total, created = Slot.objects.bulk_create_slots(instr, start_date, start_time, end_time, duration,
                                                            day_count)

            if total == created:
                messages.success(
                    request, "All slots were created successfully.")
            else:
                messages.warning(request, f"{created} out of {total} slots created. Some slots may not have been created"
                                          f" due to clashes with existing slots.")
            return redirect("..")
        else:
            form = BulkCreateSlotsForm()
            return SlotAdmin.render_bulk_slots_form(request, form)
