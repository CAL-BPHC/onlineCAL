from booking_portal.models.instrument.requests import BET
from django import forms

from .base import UserDetailsForm, UserRemarkForm


class BETForm(UserDetailsForm, UserRemarkForm):
    title = "Brunauer-Emmett-Teller"
    subtitle = "Brunauer-Emmett-Teller (BET), Microtrac Bel BEL-SORP mini II"
    help_text = """
    <b>Please provide any other information in other remarks (eg. toxic samples) </b>
    """

    class Meta(UserDetailsForm.Meta, UserRemarkForm.Meta):
        model = BET
        fields = (
            UserDetailsForm.Meta.fields
            + (
                "sample_code",
                "pretreatment_conditions",
                "precautions",
                "adsorption",
                "surface_area",
            )
            + UserRemarkForm.Meta.fields
        )

        labels = dict(
            **UserDetailsForm.Meta.labels,
            **UserRemarkForm.Meta.labels,
            **{
                "sample_code": "Sample Code",
                "pretreatment_conditions": "Pretreatment Conditions",
                "precautions": "Precautions to be taken",
                "adsorption": "N2 / CO2 Adsorption",
                "surface_area": "Specific surface area / surface area and pore size analysis to be required",
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
                "pretreatment_conditions": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "precautions": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "adsorption": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "surface_area": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
            },
        )
