from django import forms

from booking_portal.models.instrument.requests import HighPressureGasAdsorption

from .base import UserDetailsForm, UserRemarkForm


class HighPressureGasAdsorptionForm(UserDetailsForm, UserRemarkForm):
    title = "High Pressure Gas Adsorption Instrument"
    subtitle = "High Pressure Gas Adsorption Instrument"
    help_text = """
    Note: Mention the proper activation condition before the measurement.
    <br><b>Please provide any other important information in other remarks (e.g. toxic samples)</b>
    """

    class Meta(UserDetailsForm.Meta, UserRemarkForm.Meta):
        model = HighPressureGasAdsorption
        fields = (
            UserDetailsForm.Meta.fields
            + (
                "sample_codes",
                "sample_type",
                "activation_temperature",
                "activation_time",
                "required_gas",
                "temperature",
                "pressure_range_start",
                "pressure_range_end",
            )
            + UserRemarkForm.Meta.fields
        )

        labels = dict(
            **UserDetailsForm.Meta.labels,
            **UserRemarkForm.Meta.labels,
            sample_codes="Sample Codes",
            sample_type="Sample Type",
            activation_temperature="Activation Temperature (°C)",
            activation_time="Activation Time (h)",
            required_gas="Required Gas",
            temperature="Temperature (°C)",
            pressure_range_start="Pressure Range Start (bar)",
            pressure_range_end="Pressure Range End (bar)",
        )

        widgets = dict(
            **UserDetailsForm.Meta.widgets,
            **UserRemarkForm.Meta.widgets,
            sample_codes=forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            sample_type=forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            activation_temperature=forms.NumberInput(
                attrs={
                    "class": "form-control",
                }
            ),
            activation_time=forms.NumberInput(
                attrs={
                    "class": "form-control",
                }
            ),
            required_gas=forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            temperature=forms.NumberInput(
                attrs={
                    "class": "form-control",
                }
            ),
            pressure_range_start=forms.NumberInput(
                attrs={
                    "class": "form-control",
                }
            ),
            pressure_range_end=forms.NumberInput(
                attrs={
                    "class": "form-control",
                }
            ),
        )
