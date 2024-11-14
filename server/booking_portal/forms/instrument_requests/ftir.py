from booking_portal.models.instrument.requests import FTIR
from django import forms

from .base import UserDetailsForm, UserRemarkForm


class FTIRForm(UserDetailsForm, UserRemarkForm):
    title = "Fourier Transform Infrared Spectrometer"
    subtitle = "Fourier Transform Infrared Spectrometer"
    help_text = """Note: the minimum amount of the sample should be 2 mg.
    """

    class Meta(UserDetailsForm.Meta, UserRemarkForm.Meta):
        model = FTIR
        fields = (
            UserDetailsForm.Meta.fields
            + (
                "sample_code",
                "composition",
                "state",
                "solvent",
            )
            + UserRemarkForm.Meta.fields
        )

        labels = dict(
            **UserDetailsForm.Meta.labels,
            **UserRemarkForm.Meta.labels,
            **{
                "sample_code": "Sample Code",
                "composition": "Composition",
                "state": "Solid / Liquid",
                "solvent": "Solvent Used (if any)",
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
                "composition": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "state": forms.Select(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "solvent": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
            },
        )
