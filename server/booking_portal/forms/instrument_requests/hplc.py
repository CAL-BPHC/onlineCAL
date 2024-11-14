from booking_portal.models.instrument.requests import HPLC
from django import forms

from .base import UserDetailsForm, UserRemarkForm


class HPLCForm(UserDetailsForm, UserRemarkForm):
    title = "HPLC-Shimadzu"
    subtitle = "HPLC-Shimadzu UFLC"
    help_text = """
    <b>Please provide any other information in other remarks (eg. toxic samples) </b>
    """

    class Meta(UserDetailsForm.Meta, UserRemarkForm.Meta):
        model = HPLC
        fields = (
            UserDetailsForm.Meta.fields
            + (
                "sample_code",
                "sample_information",
                "mobile_phase",
                "column_for_lc",
                "detection_wavelength",
            )
            + UserRemarkForm.Meta.fields
        )

        labels = dict(
            **UserDetailsForm.Meta.labels,
            **UserRemarkForm.Meta.labels,
            **{
                "sample_code": "Sample Code",
                "sample_information": "Sample information / composition",
                "mobile_phase": "Mobile Phase Composition",
                "column_for_lc": "Column for LC",
                "detection_wavelength": "Detection Wavelength(s)",
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
                "sample_information": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "mobile_phase": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "column_for_lc": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "detection_wavelength": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
            },
        )
