from ... import forms
from .user import CustomUserAdmin
from ...models import Faculty


class FacultyAdmin(CustomUserAdmin):
    CSV_HEADERS_FACULTY = ('department',)

    form = forms.FacultyChangeForm
    add_form = forms.FacultyCreationForm

    list_filter = CustomUserAdmin.list_filter + ('department',)
    list_display = CustomUserAdmin.list_display + ('department',)
    fieldsets = CustomUserAdmin.fieldsets + (
        (None, {'fields': ('department',)},),
    )
    add_fieldsets = CustomUserAdmin.add_fieldsets + (
        (None, {
            'classes': ('wide',),
            'fields': ('department',)}
         ),
    )

    def _validate_record(self, record):
        return super()._validate_record(record)

    def get_user_type(self, request):
        return Faculty

    def is_user_staff(self):
        return False

    def get_csv_headers(self):
        return super().get_csv_headers() + self.CSV_HEADERS_FACULTY
