import csv
from io import StringIO
from itertools import chain

from booking_portal.models.faculty_request import FacultyRequest
from booking_portal.models.request import StudentRequest
from django.contrib import admin, messages
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import path, reverse

from ..forms import InstrumentChangeForm, InstrumentCreateForm, UtilisationReportForm
from ..reporting import request_hours, safe_total_cost
from ..models import CustomUser, Instrument

DETAILED_REPORT_TITLE = "Download Detailed Usage Report"


class InstrumentAdmin(admin.ModelAdmin):
    form = InstrumentChangeForm
    add_form = InstrumentCreateForm
    list_filter = admin.ModelAdmin.list_filter + ("status",)
    list_display = admin.ModelAdmin.list_display + ("status",)
    actions = ("instrument_usage_report_action", "detailed_usage_report_action")
    change_form_template = "admin/instrument_change_form.html"

    # only superuser has permission to add instruments
    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        return False

    @staticmethod
    @user_passes_test(
        lambda u: u.is_authenticated and (u.role == "PORTAL_ADMIN" or u.is_superuser)
    )
    def instrument_usage_report_form(request):
        info = Instrument._meta.app_label, Instrument._meta.model_name
        instruments = request.GET.get("instruments", "")
        try:
            instruments = Instrument.objects.filter(pk__in=instruments.split(","))
        except ValidationError:
            messages.error(request, "Invalid instruments")
            return redirect(reverse("admin:%s_%s_changelist" % info))

        if request.method == "POST":
            form = UtilisationReportForm(request.POST)
            if not form.is_valid():
                return InstrumentAdmin.render_instrument_usage_report_form(
                    request, form
                )

            start_date = form.cleaned_data["start_date"]
            end_date = form.cleaned_data["end_date"]

            csv_file = StringIO()
            Instrument.objects.export_instrument_usage_report(
                csv_file, instruments, start_date, end_date
            )
            response = HttpResponse(csv_file.getvalue(), content_type="text/csv")
            response["Content-Disposition"] = 'attachment; filename="Usage Report.csv"'

            csv_file.close()
            return response
        else:
            form = UtilisationReportForm()
            return InstrumentAdmin.render_instrument_usage_report_form(request, form)

    def detailed_usage_report_form(self, request):
        """One CSV row per booking, for every selected instrument at once."""
        if not (
            request.user.role == CustomUser.Role.PORTAL_ADMIN
            or request.user.is_superuser
        ):
            raise PermissionDenied
        info = Instrument._meta.app_label, Instrument._meta.model_name
        instruments = request.GET.get("instruments", "")
        try:
            instruments = Instrument.objects.filter(pk__in=instruments.split(","))
        except ValidationError:
            messages.error(request, "Invalid instruments")
            return redirect(reverse("admin:%s_%s_changelist" % info))

        if request.method == "POST":
            form = UtilisationReportForm(request.POST)
            if not form.is_valid():
                return InstrumentAdmin.render_instrument_usage_report_form(
                    request, form, DETAILED_REPORT_TITLE
                )

            start_date = form.cleaned_data["start_date"]
            end_date = form.cleaned_data["end_date"]

            csv_file = StringIO()
            InstrumentAdmin.create_detailed_usage_report(
                instruments, start_date, end_date, csv_file
            )
            response = HttpResponse(csv_file.getvalue(), content_type="text/csv")
            response["Content-Disposition"] = (
                'attachment; filename="Detailed Usage Report '
                f'{start_date} to {end_date}.csv"'
            )

            csv_file.close()
            return response
        else:
            form = UtilisationReportForm()
            return InstrumentAdmin.render_instrument_usage_report_form(
                request, form, DETAILED_REPORT_TITLE
            )

    @staticmethod
    def create_detailed_usage_report(instruments, start_date, end_date, csv_file):
        """Write every student and faculty booking as its own row.

        Columns are kept atomic (separate date, time and duration fields, no
        combined slot description) so the output can be pivoted directly.
        """
        headers = (
            "Request ID",
            "Request Type",
            "Instrument",
            "Department",
            "Faculty",
            "Student",
            "Date",
            "Start Time",
            "End Time",
            "Duration (hours)",
            "Status",
            "Total Cost",
        )
        writer = csv.DictWriter(csv_file, headers)
        writer.writeheader()

        related = ("slot", "instrument", "faculty", "faculty__department")
        student_requests = StudentRequest.objects.filter(
            instrument__in=instruments,
            slot__date__gte=start_date,
            slot__date__lte=end_date,
        ).select_related(*related, "student")

        faculty_requests = FacultyRequest.objects.filter(
            instrument__in=instruments,
            slot__date__gte=start_date,
            slot__date__lte=end_date,
        ).select_related(*related)

        requests = sorted(
            chain(
                ((req, "Student") for req in student_requests),
                ((req, "Faculty") for req in faculty_requests),
            ),
            key=lambda pair: (
                pair[0].instrument.name,
                pair[0].slot.date,
                pair[0].slot.start_time,
            ),
        )

        for req, request_type in requests:
            department = req.faculty.department
            writer.writerow(
                {
                    "Request ID": f"{request_type[0]}{req.id}",
                    "Request Type": request_type,
                    "Instrument": req.instrument.name,
                    "Department": department.name.title() if department else "-",
                    "Faculty": req.faculty,
                    "Student": req.student if request_type == "Student" else "-",
                    "Date": req.slot.date.isoformat(),
                    "Start Time": req.slot.start_time,
                    "End Time": req.slot.end_time,
                    "Duration (hours)": round(request_hours(req), 2),
                    "Status": req.get_status_display(),
                    "Total Cost": safe_total_cost(req, default=""),
                }
            )

    def changeform_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context["utilisation_report"] = True
        extra_context["utilisation_report_url"] = "admin:instrument_utilisation_report"
        extra_context["object_id"] = object_id
        return super().changeform_view(request, object_id, form_url, extra_context)

    def get_urls(self):
        urls = super().get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name

        my_urls = [
            path(
                "usage-report/",
                InstrumentAdmin.instrument_usage_report_form,
                name="%s_%s_usage-report" % info,
            ),
            path(
                "detailed-usage-report/",
                self.admin_site.admin_view(self.detailed_usage_report_form),
                name="%s_%s_detailed-usage-report" % info,
            ),
            path(
                "report/instrument/<int:instrument_id>",
                self.admin_site.admin_view(self.export_utilisation_report),
                name="instrument_utilisation_report",
            ),
        ]
        return my_urls + urls

    def export_utilisation_report(self, request, instrument_id):
        if not (
            request.user.role == CustomUser.Role.PORTAL_ADMIN
            or request.user.is_superuser
        ):
            raise PermissionDenied
        instrument = self.get_object(request, instrument_id)
        if request.method == "POST":
            form = UtilisationReportForm(request.POST)
            if not form.is_valid():
                return render(
                    request,
                    "admin/utilisation_report_entity.html",
                    {
                        "form": form,
                        "instrument": instrument,
                        "cancel_url": "admin:booking_portal_instrument_changelist",
                    },
                )
            start_date = form.cleaned_data["start_date"]
            end_date = form.cleaned_data["end_date"]

            csv_file = StringIO()
            self.create_utilisation_report(instrument, start_date, end_date, csv_file)
            response = HttpResponse(csv_file.getvalue(), content_type="text/csv")
            response["Content-Disposition"] = (
                f'attachment; filename="{instrument.name} Utilisation Report.csv"'
            )
            csv_file.close()
            return response

        else:
            form = UtilisationReportForm()
            return render(
                request,
                "admin/utilisation_report_entity.html",
                {
                    "form": form,
                    "instrument": instrument,
                    "cancel_url": "admin:booking_portal_instrument_changelist",
                },
            )

    def create_utilisation_report(self, instrument, start_date, end_date, csv_file):
        headers = (
            "Request ID",
            "Faculty",
            "Student",
            "Department",
            "Slot",
            "Total Cost",
            "Status",
        )
        writer = csv.DictWriter(csv_file, headers)
        writer.writeheader()

        student_requests = StudentRequest.objects.filter(
            instrument=instrument,
            slot__date__gte=start_date,
            slot__date__lte=end_date,
        ).select_related("slot")

        faculty_requests = FacultyRequest.objects.filter(
            instrument=instrument,
            slot__date__gte=start_date,
            slot__date__lte=end_date,
        ).select_related("slot")

        requests = student_requests.union(faculty_requests).order_by(
            "slot__date", "slot__start_time"
        )

        for req in requests:
            writer.writerow(
                {
                    "Request ID": req.id,
                    "Faculty": req.faculty,
                    "Student": req.student if hasattr(req, "student") else "-",
                    "Department": req.faculty.department.name.title(),
                    "Slot": req.slot,
                    "Total Cost": req.total_cost,
                    "Status": req.get_status_display(),
                }
            )

    @admin.action(description="Download Instrument Usage Report")
    def instrument_usage_report_action(self, request, queryset):
        return self._redirect_to_report(queryset, "usage-report")

    @admin.action(description="Download Detailed Usage Report (one row per booking)")
    def detailed_usage_report_action(self, request, queryset):
        return self._redirect_to_report(queryset, "detailed-usage-report")

    def _redirect_to_report(self, queryset, url_name):
        selected = queryset.values_list("pk", flat=True)
        opts = self.model._meta
        url = "%s?instruments=%s" % (
            reverse(
                "admin:%s_%s_%s" % (opts.app_label, opts.model_name, url_name),
            ),
            ",".join([str(pk) for pk in selected]),
        )
        return redirect(url)

    instrument_usage_report_action.short_description = (
        "Download Instrument Usage Report"
    )

    @staticmethod
    def render_instrument_usage_report_form(
        request, form, title="Download Instrument Usage Report"
    ):
        payload = {
            "form": form,
            "opts": Instrument._meta,
            "has_view_permission": True,
            "title": title,
        }
        return render(request, "admin/instrument_usage_report_form.html", payload)
