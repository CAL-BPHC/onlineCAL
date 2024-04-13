from io import StringIO

from django.contrib import admin, messages
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import path, reverse

from .. import permissions
from ..forms import (InstrumentChangeForm, InstrumentCreateForm,
                     InstrumentUsageReportForm)
from ..models import Instrument


class InstrumentAdmin(admin.ModelAdmin):
    form = InstrumentChangeForm
    add_form = InstrumentCreateForm
    list_filter = admin.ModelAdmin.list_filter + ('status',)
    actions = ('instrument_usage_report_action', )

    # only superuser has permission to add instruments
    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        return False

    @staticmethod
    @user_passes_test(lambda u: permissions.is_lab_assistant(u) or u.is_superuser)
    def instrument_usage_report_form(request):
        info = Instrument._meta.app_label, Instrument._meta.model_name
        instruments = request.GET.get('instruments', '')
        try:
            instruments = Instrument.objects.filter(
                pk__in=instruments.split(','))
        except ValidationError as e:
            messages.error(request, "Invalid instruments")
            return redirect(reverse('admin:%s_%s_changelist' % info))

        if request.method == 'POST':
            form = InstrumentUsageReportForm(request.POST)
            if not form.is_valid():
                return InstrumentAdmin.render_bulk_slots_form(request, form)

            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']

            csv_file = StringIO()
            Instrument.objects.export_instrument_usage_report(
                csv_file, instruments, start_date, end_date)
            response = HttpResponse(
                csv_file.getvalue(), content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="Usage Report.csv"'

            csv_file.close()
            return response
        else:
            form = InstrumentUsageReportForm()
            return InstrumentAdmin.render_instrument_usage_report_form(request, form)

    def get_urls(self):
        urls = super().get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name

        my_urls = [
            path("usage-report/", InstrumentAdmin.instrument_usage_report_form,
                 name='%s_%s_usage-report' % info)
        ]
        return my_urls + urls

    @admin.action(description='Download Instrument Usage Report')
    def instrument_usage_report_action(self, request, queryset):
        selected = queryset.values_list('pk', flat=True)
        opts = self.model._meta
        url = '%s?instruments=%s' % (
            reverse(
                'admin:%s_%s_usage-report' % (opts.app_label, opts.model_name),
            ),
            ",".join([str(pk) for pk in selected])
        )
        return redirect(url)
    instrument_usage_report_action.short_description = 'Download Instrument Usage Report'

    @staticmethod
    def render_instrument_usage_report_form(request, form):
        payload = {
            "form": form,
            "opts": Instrument._meta,
            "has_view_permission": True,
        }
        return render(request, "admin/instrument_usage_report_form.html", payload)
