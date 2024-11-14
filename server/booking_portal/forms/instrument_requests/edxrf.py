from booking_portal.models.instrument.requests import EDXRF
from django import forms

from .base import UserDetailsForm, UserRemarkForm


class EDXRFForm(UserDetailsForm, UserRemarkForm):
    title = "Energy Dispersive X-RAY Fluorescence"
    subtitle = "Energy Dispersive X-RAY Fluorescence"
    help_text = """
    <b>Please provide any other information in other remarks (eg. toxic samples) </b>
    """

    class Meta(UserDetailsForm.Meta, UserRemarkForm.Meta):
        model = EDXRF
        fields = (
            UserDetailsForm.Meta.fields
            + (
                "sample_code",
                "sample_nature",
                "elements_present",
            )
            + UserRemarkForm.Meta.fields
        )

        labels = dict(
            **UserDetailsForm.Meta.labels,
            **UserRemarkForm.Meta.labels,
            **{
                "sample_code": "Sample Code",
                "sample_nature": "Nature of Sample",
                "elements_present": "Elements Present",
            },
        )

        widgets = dict(
            **UserDetailsForm.Meta.widgets,
            **UserRemarkForm.Meta.widgets,
            **{
                "sample_code": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "sample_nature": forms.Select(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "elements_present": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
            },
        )
