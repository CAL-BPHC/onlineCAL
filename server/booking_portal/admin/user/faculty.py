from django.contrib.contenttypes.models import ContentType
from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.urls import path

from booking_portal.forms.admin import TopUpForm
from booking_portal.models.user import BalanceTopUpLog

from ... import forms
from ...models import CustomUser, Faculty
from .user import CustomUserAdmin


class FacultyAdmin(CustomUserAdmin):
    CSV_HEADERS_FACULTY = ("department",)
    change_form_template = "admin/top_up_change_form.html"
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
        return super()._validate_record(record)

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
            )
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
            form = TopUpForm()
            context = {
                "form": form,
                "faculty": faculty,
                "cancel_url": "admin:booking_portal_faculty_changelist",
            }
        return render(request, "admin/top_up_entity.html", context)

    def changeform_view(
        self, request: HttpRequest, object_id, form_url="", extra_context=None
    ):
        extra_context = extra_context or {}
        extra_context["top_up_wallet"] = True
        extra_context["top_up_url"] = "admin:faculty_top_up"
        extra_context["faculty_id"] = object_id
        return super().changeform_view(request, object_id, form_url, extra_context)
