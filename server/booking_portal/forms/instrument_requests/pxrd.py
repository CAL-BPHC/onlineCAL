from booking_portal.models.instrument.requests import PXRD
from django import forms

from .base import UserDetailsForm, UserRemarkForm


class PXRDForm(UserDetailsForm, UserRemarkForm):
    title = "Powder X-RAY Diffractometer"
    subtitle = "Powder X-RAY Diffractometer (RIGAKU ULTIMA-IV)"
    help_text = """
    <b>Please provide any other information in other remarks (eg. toxic samples) </b>
    """

    class Meta(UserDetailsForm.Meta, UserRemarkForm.Meta):
        model = PXRD
        fields = (
            UserDetailsForm.Meta.fields
            + (
                "sample_code",
                "chemical_composition",
                "sample_description",
                "range",
                "scanning_rate",
            )
            + UserRemarkForm.Meta.fields
        )

        labels = dict(
            **UserDetailsForm.Meta.labels,
            **UserRemarkForm.Meta.labels,
            **{
                "sample_code": "Sample Code",
                "chemical_composition": "Chemical Composition",
                "sample_description": "Sample Description (Film/ Powder/ Pellet)",
                "range": "2-theta Range",
                "scanning_range": "Scanning Rate (degree/min)",
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
                "sample_description": forms.Select(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "range": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "scanning_rate": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
            },
        )
