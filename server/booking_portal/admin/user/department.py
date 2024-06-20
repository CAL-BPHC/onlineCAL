from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.urls import path

from booking_portal.forms.admin import TopUpForm

from ...models import CustomUser, Department
from .user import CustomUserAdmin


class DepartmentAdmin(CustomUserAdmin):
    list_display = CustomUserAdmin.list_display + ("balance",)
    change_form_template = "admin/top_up_change_form.html"
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
            )
        ]

    def top_up_balance(self, request, department_id):
        department = self.get_object(request, department_id)
        if request.method == "POST":
            form = TopUpForm(request.POST)
            if form.is_valid():
                amount = form.cleaned_data["top_up_amount"]
                department.balance += amount
                department.save()
                self.message_user(
                    request, f"{department} balance topped up by {amount} successfully."
                )
                return redirect("admin:booking_portal_department_change", department_id)
        else:
            form = TopUpForm()
            context = {
                "form": form,
                "faculty": department,
                "cancel_url": "admin:booking_portal_department_changelist",
            }
        return render(request, "admin/top_up_entity.html", context)

    def changeform_view(
        self, request: HttpRequest, object_id, form_url="", extra_context=None
    ):
        extra_context = extra_context or {}
        extra_context["top_up_wallet"] = True
        extra_context["top_up_url"] = "admin:department_top_up"
        extra_context["object_id"] = object_id
        return super().changeform_view(request, object_id, form_url, extra_context)
