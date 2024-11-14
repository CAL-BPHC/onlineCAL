from booking_portal.models.instrument.requests import SCXRD
from django import forms

from .base import UserDetailsForm, UserRemarkForm


class SCXRDForm(UserDetailsForm, UserRemarkForm):
    title = "Single Crystal X-RAY Diffractometer"
    subtitle = "Single Crystal X-RAY Diffractometer RIGAKU Oxford XTALAB"
    help_text = """
    <b>Please provide any other information in other remarks (eg. toxic samples) </b>
    """

    class Meta(UserDetailsForm.Meta, UserRemarkForm.Meta):
        model = SCXRD
        fields = (
            UserDetailsForm.Meta.fields
            + (
                "sample_code",
                "chemical_composition",
                "scanning_rate",
                "source",
            )
            + UserRemarkForm.Meta.fields
        )

        labels = dict(
            **UserDetailsForm.Meta.labels,
            **UserRemarkForm.Meta.labels,
            **{
                "sample_code": "Sample Code",
                "chemical_composition": "Chemical Composition",
                "scanning_rate": "Scanning Rate",
                "source": "X-ray source to be used (Cu or Mo)",
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
                "chemical_composition": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "scanning_rate": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "source": forms.Select(
                    attrs={
                        "class": "form-control",
                    }
                ),
            },
        )
