from ... import forms
from ...models import CustomUser, Faculty
from .user import CustomUserAdmin


class FacultyAdmin(CustomUserAdmin):
    CSV_HEADERS_FACULTY = ("department",)

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
