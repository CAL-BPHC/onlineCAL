"""Atomic Absorption Spectroscopy"""

from booking_portal.models.instrument.requests import AAS
from django import forms

from .base import UserDetailsForm, UserRemarkForm


class AASForm(UserDetailsForm, UserRemarkForm):
    title = "Atomic Absorption Spectroscopy"
    subtitle = "Atomic Absorption Spectroscopy"
    help_text = """
    <b>Lamps Available:</b> As, Ba, Cd, Cr, Cu, Fe ...etc <br>
        Sample quality required is 1mg/ml (10ml) <br>
        Note: Sample should be submitted in uniform and homogeneous liquid. Solid and other than liquid samples are need to be dissolved or digested in acid (concentrated or diluted). <br>
        <b>Please provide any other important information in other remarks (eg. toxic samples)</b>
    """

    class Meta(UserDetailsForm.Meta, UserRemarkForm.Meta):
        model = AAS
        fields = (
            *UserDetailsForm.Meta.fields,
            "sample_code",
            "elements",
            *UserRemarkForm.Meta.fields,
        )

        labels = dict(
            **UserDetailsForm.Meta.labels,
            **UserRemarkForm.Meta.labels,
            **{
                "sample_code": "Sample Code",
                "elements": "Elements to be Analyzed",
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
                "elements": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
            },
        )
