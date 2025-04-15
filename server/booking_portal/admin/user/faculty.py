import csv
from io import StringIO

from booking_portal.forms.admin import TopUpForm, UtilisationReportForm
from booking_portal.models.user import BalanceTopUpLog, Department
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import validate_email
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import path

from ... import forms
from ...models import CustomUser, Faculty
from ...models.faculty_request import FacultyRequest
from ...models.request import StudentRequest
from .user import CustomUserAdmin


class FacultyAdmin(CustomUserAdmin):
    CSV_HEADERS_FACULTY = ("department",)
    change_form_template = "admin/top_up_utilisation_change_form.html"
    form = forms.FacultyChangeForm
    add_form = forms.FacultyCreationForm

    list_filter = CustomUserAdmin.list_filter + ("department",)
    list_display = CustomUserAdmin.list_display + ("department", "balance")
    fieldsets = CustomUserAdmin.fieldsets + (
        (
            None,
            {"fields": ("department", "balance")},
        ),
    )
    add_fieldsets = CustomUserAdmin.add_fieldsets + (
        (None, {"classes": ("wide",), "fields": ("department", "balance")}),
    )

    def _validate_record(self, record):
        record = super()._validate_record(record)

        record["department"] = record["department"].strip()
        validate_email(record["department"])

        try:
            obj = Department.objects.get(email=record["department"])
        except Department.DoesNotExist:
            raise ObjectDoesNotExist(
                f"Department doesn't exist: \"{record['department']}\""
            )

        record["department"] = obj
        return record

    def get_user_type(self, request):
        return Faculty

    def is_user_staff(self):
        return False

    def get_csv_headers(self):
        return super().get_csv_headers() + self.CSV_HEADERS_FACULTY

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj is None:
            form.base_fields["role"].initial = CustomUser.Role.FACULTY
            form.base_fields["role"].disabled = True
        return form

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["balance"]
        return super().get_readonly_fields(request, obj)

    def get_urls(self):
        return super().get_urls() + [
            path(
                "topup/faculty/<int:faculty_id>",
                self.admin_site.admin_view(self.top_up_balance),
                name="faculty_top_up",
            ),
            path(
                "report/faculty/<int:faculty_id>",
                self.admin_site.admin_view(self.export_utilisation_report),
                name="faculty_utilisation_report",
            ),
        ]

    def top_up_balance(self, request, faculty_id):
        faculty = self.get_object(request, faculty_id)
        if request.method == "POST":
            form = TopUpForm(request.POST)
            if form.is_valid():
                amount = form.cleaned_data["top_up_amount"]
                faculty.balance += amount
                faculty.save()
                BalanceTopUpLog.objects.create(
                    admin_user=request.user,
                    top_up_amount=amount,
                    content_type=ContentType.objects.get_for_model(faculty.__class__),
                    object_id=faculty.id,
                )
                self.message_user(
                    request, f"{faculty} balance topped up by {amount} successfully."
                )
                return redirect("admin:booking_portal_faculty_change", faculty_id)
            else:
                return render(
                    request,
                    "admin/top_up_entity.html",
                    {
                        "form": form,
                        "faculty": faculty,
                        "cancel_url": "admin:booking_portal_faculty_changelist",
                    },
                )
        else:
            form = TopUpForm()
            context = {
                "form": form,
                "faculty": faculty,
                "cancel_url": "admin:booking_portal_faculty_changelist",
            }
        return render(request, "admin/top_up_entity.html", context)

    def create_utilisation_report(self, faculty, start_date, end_date):
        csv_file = StringIO()
        headers = (
            "Request ID",
            "Student",
            "Instrument",
            "Slot",
            "Total Cost",
            "Status",
        )
        writer = csv.DictWriter(csv_file, headers)
        writer.writeheader()

        student_requests = StudentRequest.objects.filter(
            student__supervisor=faculty,
            slot__date__gte=start_date,
            slot__date__lte=end_date,
        ).select_related("slot")

        faculty_requests = FacultyRequest.objects.filter(
            faculty=faculty,
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
                    "Student": req.student if hasattr(req, "student") else "-",
                    "Instrument": req.instrument,
                    "Slot": req.slot,
                    "Total Cost": req.total_cost,
                    "Status": req.get_status_display(),
                }
            )
        return csv_file

    def export_utilisation_report(self, request, faculty_id):
        faculty = self.get_object(request, faculty_id)
        if request.method == "POST":
            form = UtilisationReportForm(request.POST)
            if not form.is_valid():
                return render(
                    request,
                    "admin/utilisation_report_entity.html",
                    {
                        "form": form,
                        "faculty": faculty,
                        "cancel_url": "admin:booking_portal_faculty_changelist",
                    },
                )
            start_date = form.cleaned_data["start_date"]
            end_date = form.cleaned_data["end_date"]

            csv_file = self.create_utilisation_report(faculty, start_date, end_date)
            response = HttpResponse(csv_file.getvalue(), content_type="text/csv")
            response["Content-Disposition"] = (
                f'attachment; filename="{faculty.name.title()} Utilisation Report.csv"'
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
                    "faculty": faculty,
                    "cancel_url": "admin:booking_portal_faculty_changelist",
                },
            )

    def changeform_view(
        self, request: HttpRequest, object_id, form_url="", extra_context=None
    ):
        extra_context = extra_context or {}
        extra_context["top_up_wallet"] = True
        extra_context["top_up_url"] = "admin:faculty_top_up"
        extra_context["utilisation_report"] = True
        extra_context["utilisation_report_url"] = "admin:faculty_utilisation_report"
        extra_context["faculty_id"] = object_id
        return super().changeform_view(request, object_id, form_url, extra_context)
