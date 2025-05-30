import csv
from io import StringIO

from booking_portal.forms.admin import TopUpForm, UtilisationReportForm
from booking_portal.models.user import BalanceTopUpLog
from django.contrib.contenttypes.models import ContentType
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import path

from ...models import CustomUser, Department
from ...models.faculty_request import FacultyRequest
from ...models.request import StudentRequest
from .user import CustomUserAdmin


class DepartmentAdmin(CustomUserAdmin):
    list_display = CustomUserAdmin.list_display + ("balance",)
    change_form_template = "admin/top_up_utilisation_change_form.html"
    fieldsets = CustomUserAdmin.fieldsets + (
        (
            None,
            {"fields": ("balance",)},
        ),
    )
    add_fieldsets = CustomUserAdmin.add_fieldsets + (
        (None, {"classes": ("wide",), "fields": ("balance",)}),
    )

    def has_add_permission(self, request) -> bool:
        return request.user.is_staff

    def has_change_permission(self, request, obj=None) -> bool:
        return request.user.is_staff

    def get_user_type(self, request):
        return Department

    def is_user_staff(self):
        return False

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj is None:
            form.base_fields["role"].initial = CustomUser.Role.DEPARTMENT
            form.base_fields["role"].disabled = True
        return form

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["balance"]
        return super().get_readonly_fields(request, obj)

    def get_urls(self):
        return super().get_urls() + [
            path(
                "topup/faculty/<int:department_id>",
                self.admin_site.admin_view(self.top_up_balance),
                name="department_top_up",
            ),
            path(
                "report/faculty/<int:department_id>",
                self.admin_site.admin_view(self.export_utilisation_report),
                name="department_utilisation_report",
            ),
        ]

    def top_up_balance(self, request, department_id):
        department = self.get_object(request, department_id)
        if request.method == "POST":
            form = TopUpForm(request.POST)
            if form.is_valid():
                amount = form.cleaned_data["top_up_amount"]
                department.balance += amount
                department.save()
                BalanceTopUpLog.objects.create(
                    admin_user=request.user,
                    top_up_amount=amount,
                    content_type=ContentType.objects.get_for_model(
                        department.__class__
                    ),
                    object_id=department.id,
                )
                self.message_user(
                    request, f"{department} balance topped up by {amount} successfully."
                )
                return redirect("admin:booking_portal_department_change", department_id)
            else:
                return render(
                    request,
                    "admin/top_up_entity.html",
                    {
                        "form": form,
                        "faculty": department,
                        "cancel_url": "admin:booking_portal_department_changelist",
                    },
                )
        else:
            form = TopUpForm()
            context = {
                "form": form,
                "faculty": department,
                "cancel_url": "admin:booking_portal_department_changelist",
            }
        return render(request, "admin/top_up_entity.html", context)

    def create_utilisation_report(self, department, start_date, end_date):
        csv_file = StringIO()
        headers = (
            "Request ID",
            "Faculty",
            "Student",
            "Instrument",
            "Slot",
            "Total Cost",
            "Status",
        )
        writer = csv.DictWriter(csv_file, headers)
        writer.writeheader()

        student_requests = StudentRequest.objects.filter(
            student__supervisor__department=department,
            slot__date__gte=start_date,
            slot__date__lte=end_date,
        ).select_related("slot")

        faculty_requests = FacultyRequest.objects.filter(
            faculty__department=department,
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
                    "Instrument": req.instrument,
                    "Slot": req.slot,
                    "Total Cost": req.total_cost,
                    "Status": req.get_status_display(),
                }
            )
        return csv_file

    def export_utilisation_report(self, request, department_id):
        department = self.get_object(request, department_id)
        if request.method == "POST":
            form = UtilisationReportForm(request.POST)
            if not form.is_valid():
                return render(
                    request,
                    "admin/utilisation_report_entity.html",
                    {
                        "form": form,
                        "faculty": department,
                        "cancel_url": "admin:booking_portal_department_changelist",
                    },
                )
            start_date = form.cleaned_data["start_date"]
            end_date = form.cleaned_data["end_date"]

            csv_file = self.create_utilisation_report(department, start_date, end_date)
            response = HttpResponse(csv_file.getvalue(), content_type="text/csv")
            response["Content-Disposition"] = (
                f'attachment; filename="{department.name.title()} Utilisation Report.csv"'
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
                    "faculty": department,
                    "cancel_url": "admin:booking_portal_department_changelist",
                },
            )

    def changeform_view(
        self, request: HttpRequest, object_id, form_url="", extra_context=None
    ):
        extra_context = extra_context or {}
        extra_context["top_up_wallet"] = True
        extra_context["top_up_url"] = "admin:department_top_up"
        extra_context["utilisation_report"] = True
        extra_context["utilisation_report_url"] = "admin:department_utilisation_report"
        extra_context["object_id"] = object_id
        return super().changeform_view(request, object_id, form_url, extra_context)
