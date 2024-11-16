from booking_portal.models.instrument.requests import LSCM
from django import forms

from .base import UserDetailsForm, UserRemarkForm


class LSCMForm(UserDetailsForm, UserRemarkForm):
    title = "Laser Scanning Confocal Microscopy"
    subtitle = "Laser Scanning Confocal Microscopy (Leica DMi8)"
    help_text = """
    <b>Note:</b><br>
        1. For live sampling images, please mention the time required for analysis.<br>
        2. Analysis details: Whether fluorescence/ transmission/ reflection imaging and Z sectioning or time lapse is required/not.<br>
        <b>Please provide any other information in other remarks (eg. toxic samples) </b>
    """

    class Meta(UserDetailsForm.Meta, UserRemarkForm.Meta):
        model = LSCM
        fields = (
            UserDetailsForm.Meta.fields
            + (
                "sample_description",
                "dye",
                "excitation_wavelength",
                "emission_range",
                "analysis_details",
            )
            + UserRemarkForm.Meta.fields
        )

        labels = dict(
            **UserDetailsForm.Meta.labels,
            **UserRemarkForm.Meta.labels,
            **{
                "sample_description": "Sample Description",
                "dye": "Dye",
                "excitation_wavelength": "Excitation Wavelength",
                "emission_range": "Emission Range",
                "analysis_details": "Analysis Details",
            },
        )

        widgets = dict(
            **UserDetailsForm.Meta.widgets,
            **UserRemarkForm.Meta.widgets,
            **{
                "sample_description": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "dye": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "excitation_wavelength": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "emission_range": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "analysis_details": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
            },
        )
