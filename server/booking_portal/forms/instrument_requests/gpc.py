from booking_portal.models.instrument.requests import GPC
from django import forms

from .base import UserDetailsForm, UserRemarkForm


class GPCForm(UserDetailsForm, UserRemarkForm):
    title = "Gel Permeation chromatography"
    subtitle = "GPC (MAKE-Waters)"
    help_text = """
    <b>Please provide any other information in other remarks (eg. toxic samples) </b>
    """

    class Meta(UserDetailsForm.Meta, UserRemarkForm.Meta):
        model = GPC
        fields = (
            UserDetailsForm.Meta.fields
            + (
                "sample_code",
                "solvent_column",
                "parameters",
            )
            + UserRemarkForm.Meta.fields
        )

        labels = dict(
            **UserDetailsForm.Meta.labels,
            **UserRemarkForm.Meta.labels,
            **{
                "sample_code": "Sample Codes",
                "solvent_column": "Solvent and Column",
                "parameters": "Parameters(Flow rate,Column conditions)",
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
                "solvent_column": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "parameters": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
            },
        )
