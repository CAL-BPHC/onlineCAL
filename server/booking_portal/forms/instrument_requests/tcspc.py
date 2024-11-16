from booking_portal.models.instrument.requests import TCSPC
from django import forms

from .base import UserDetailsForm, UserRemarkForm


class TCSPCForm(UserDetailsForm, UserRemarkForm):
    title = "TCS-PC"
    subtitle = "TCS-PC"
    help_text = """
    """

    class Meta(UserDetailsForm.Meta, UserRemarkForm.Meta):
        model = TCSPC
        fields = (
            UserDetailsForm.Meta.fields
            + (
                "sample_code",
                "sample_nature",
                "chemical_composition",
            )
            + UserRemarkForm.Meta.fields
        )

        labels = dict(
            **UserDetailsForm.Meta.labels,
            **UserRemarkForm.Meta.labels,
            **{
                "sample_code": "Sample Code",
                "sample_nature": "Nature of Sample",
                "chemical_composition": "Chemical Composition",
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
                "chemical_composition": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
            },
        )
