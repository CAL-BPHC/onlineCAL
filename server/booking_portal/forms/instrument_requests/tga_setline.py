from django import forms

from booking_portal.models.instrument.requests import TGASetline

from .base import UserDetailsForm, UserRemarkForm


class TGASetlineForm(UserDetailsForm, UserRemarkForm):
    title = "Thermogravimetric Analysis, Setline"
    subtitle = "Thermogravimetric Analysis, Setline"
    help_text = """
    Note: When you are using Disposable cuvettes please clean with water only and inform Technical staff before and after the analysis.
    <br><b>Please provide any other important information in other remarks (e.g. toxic samples)</b>
    """

    class Meta(UserDetailsForm.Meta, UserRemarkForm.Meta):
        model = TGASetline
        fields = (
            UserDetailsForm.Meta.fields
            + (
                "sample_codes",
                "temp_range_start",
                "temp_range_end",
                "atmosphere",
                "heating_rate",
            )
            + UserRemarkForm.Meta.fields
        )

        labels = dict(
            **UserDetailsForm.Meta.labels,
            **UserRemarkForm.Meta.labels,
            sample_codes="Sample Codes",
            temp_range_start="Temperature Range Start (°C)",
            temp_range_end="Temperature Range End (°C)",
            atmosphere="Atmosphere",
            heating_rate="Heating Rate (°C/min)",
        )

        widgets = dict(
            **UserDetailsForm.Meta.widgets,
            **UserRemarkForm.Meta.widgets,
            sample_codes=forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            temp_range_start=forms.NumberInput(
                attrs={
                    "class": "form-control",
                }
            ),
            temp_range_end=forms.NumberInput(
                attrs={
                    "class": "form-control",
                }
            ),
            atmosphere=forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            heating_rate=forms.NumberInput(
                attrs={
                    "class": "form-control",
                }
            ),
        )
