from ...models import CustomUser, Department
from .user import CustomUserAdmin


class DepartmentAdmin(CustomUserAdmin):
    list_display = CustomUserAdmin.list_display + ("balance",)
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
