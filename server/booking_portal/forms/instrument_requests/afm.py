from booking_portal.models.instrument.requests import AFM
from django import forms

from .base import UserDetailsForm, UserRemarkForm


class AFMForm(UserDetailsForm, UserRemarkForm):
    title = "Atomic Force Microscope (AFM)"
    subtitle = "Atomic Force Microscope (AFM)"
    help_text = """
    <b>Note:</b>
    <p>Sample submission from 9.00 am to 9.15 am (Slot timings: 9.30 am to 12:30 pm)</p>
    <b>General Information:</b>
    <p>Make: Nano surf</p>
    <p>Model: Core AFM</p>
    <p>Maximum scan range: XYZ up to 100 x 100 x 12 μm</p>
    <p>Location: D-228, Chemical Engineering</p>
    """

    class Meta(UserDetailsForm.Meta, UserRemarkForm.Meta):
        model = AFM
        fields = (
            UserDetailsForm.Meta.fields
            + (
                "sample_code",
                "sample_nature",
                "imaging_mode",
            )
            + UserRemarkForm.Meta.fields
        )

        labels = dict(
            **UserDetailsForm.Meta.labels,
            **UserRemarkForm.Meta.labels,
            **{
                "sample_code": "Sample Code",
                "sample_nature": "Sample Nature",
                "imaging_mode": "Imaging Mode",
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
                "imaging_mode": forms.Select(
                    attrs={
                        "class": "form-control",
                    }
                ),
            },
        )
