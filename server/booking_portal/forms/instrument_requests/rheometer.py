from booking_portal.models.instrument.requests import Rheometer
from django import forms

from .base import UserDetailsForm, UserRemarkForm


class RheometerForm(UserDetailsForm, UserRemarkForm):
    title = "Rheometer"
    subtitle = "Rheometer, Anton Paar"
    help_text = """
    <b>Please provide any other information in other remarks (eg. toxic samples) </b>
    """

    class Meta(UserDetailsForm.Meta, UserRemarkForm.Meta):
        model = Rheometer
        fields = (
            UserDetailsForm.Meta.fields
            + (
                "sample_code",
                "ingredient_details",
                "physical_characteristics",
                "chemical_nature",
                "origin",
                "analysis_required",
            )
            + UserRemarkForm.Meta.fields
        )

        labels = dict(
            **UserDetailsForm.Meta.labels,
            **UserRemarkForm.Meta.labels,
            **{
                "sample_code": "Sample Code",
                "ingredient_details": "Details of ingredients (Solute + Solvent or Solute + Solvent + additives etc.)",
                "physical_characteristics": "Details of Pyhsical Characteristics [Concentration, gel/crystallization temperature and approx viscosity (mPa.s)]",
                "chemical_nature": "Chemical Nature of Sample (Acidic / Basic / Neutral / pH range etc.)",
                "origin": "Origin (natural or synthetic)",
                "analysis_required": "Analysis required [Viscosity, Modulus]",
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
                "ingredient_details": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "physical_characteristics": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "chemical_nature": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "origin": forms.Select(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "analysis_required": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
            },
        )
