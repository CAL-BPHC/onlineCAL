from django import forms

from booking_portal.models.instrument.requests import ContactAngle

from .base import UserDetailsForm, UserRemarkForm


class ContactAngleForm(UserDetailsForm, UserRemarkForm):
    title = "Contact Angle"
    subtitle = "Contact Angle Meter (Biolin Scientific - Attension Theta Flex)"
    help_text = '''
        <b>Please provide any other information in other remarks (eg. toxic samples).</b> <br>
        <b>Note: Inform Technical staff before and after the analysis.</b>
    '''

    class Meta(UserDetailsForm.Meta, UserRemarkForm.Meta):
        model = ContactAngle

        fields = UserDetailsForm.Meta.fields + \
            (
                "sample_codes",
                "slot_duration",
                "temperature",
                "parameters",
                "analysis_type",
                "additional_info",
            ) + \
            UserRemarkForm.Meta.fields

        labels = dict(
            **UserDetailsForm.Meta.labels,
            **UserRemarkForm.Meta.labels,
            **{
                "sample_codes": "Sample Codes",
                "slot_duration": "Slot Duration(4hr)",
                "temperature": "Temperature / Stage",
                "parameters": "Parameters",
                "analysis_type": "Type of Analysis",
                "additional_info": "Any remarks"
            }
        )

        widgets = dict(
            **UserDetailsForm.Meta.widgets,
            **UserRemarkForm.Meta.widgets,
            **{
                "sample_codes": forms.TextInput(attrs={"class": "form-control", }),
                "slot_duration": forms.TextInput(attrs={"class": "form-control", }),
                "temperature": forms.TextInput(attrs={"class": "form-control", }),
                "parameters": forms.TextInput(attrs={"class": "form-control", }),
                "analysis_type": forms.TextInput(attrs={"class": "form-control", }),
                "additional_info": forms.TextInput(attrs={"class": "form-control", }),
            }
        )
