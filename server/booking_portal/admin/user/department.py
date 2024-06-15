from ...models import CustomUser, Department
from .user import CustomUserAdmin


class DepartmentAdmin(CustomUserAdmin):
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
