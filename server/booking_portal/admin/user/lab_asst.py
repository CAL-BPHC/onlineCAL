from booking_portal.models.user import CustomUser

from ... import forms
from ...models import LabAssistant
from .user import CustomUserAdmin


class LabAssistantAdmin(CustomUserAdmin):
    CSV_HEADERS_STUDENT = ("supervisor",)

    form = forms.CustomUserChangeForm
    add_form = forms.CustomUserCreationForm

    def _validate_record(self, record):
        return super()._validate_record(record)

    def get_user_type(self, request):
        return LabAssistant

    def is_user_staff(self):
        return False

    def get_csv_headers(self):
        return super().get_csv_headers() + self.CSV_HEADERS_STUDENT

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj is None:
            form.base_fields["role"].initial = CustomUser.Role.LAB_ASSISTANT
            form.base_fields["role"].disabled = True
        return form
