from booking_portal.models.instrument.requests import TGA
from django import forms

from .base import UserDetailsForm, UserRemarkForm


class TGAForm(UserDetailsForm, UserRemarkForm):
    title = "Thermogravimetric Analysis, Shimadzu-DTG-60"
    subtitle = "Thermogravimetric Analysis, Shimadzu-DTG-60"
    help_text = """
    <b>Please provide any other information in other remarks (eg. toxic samples) </b>
    """

    class Meta(UserDetailsForm.Meta, UserRemarkForm.Meta):
        model = TGA
        fields = (
            UserDetailsForm.Meta.fields
            + (
                "sample_code",
                "chemical_composition",
                "sample_amount",
                "heating_program",
                "temperature",
                "atmosphere",
                "heating_rate",
                "sample_solubility",
            )
            + UserRemarkForm.Meta.fields
        )

        labels = dict(
            **UserDetailsForm.Meta.labels,
            **UserRemarkForm.Meta.labels,
            **{
                "sample_code": "Sample Code",
                "chemical_composition": "Chemical Composition",
                "sample_amount": "Amount of Sample / mg",
                "heating_program": "Heating program (dynamic / isothermal)",
                "temperature": "Temperature Range in Celsius",
                "atmosphere": "Atmosphere (N2, Ar, Air)",
                "heating_rate": "Heating Rate / C min-1",
                "sample_solubility": "Solubility of the sample",
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
                "sample_amount": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "heating_program": forms.Select(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "temperature": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "atmosphere": forms.Select(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "heating_rate": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "sample_solubility": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
            },
        )
