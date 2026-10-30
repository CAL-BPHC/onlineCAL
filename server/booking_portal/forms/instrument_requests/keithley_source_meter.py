from django import forms

from booking_portal.models.instrument.requests import KeithleySourceMeter

from .base import UserDetailsForm, UserRemarkForm


class KeithleySourceMeterForm(UserDetailsForm, UserRemarkForm):
    title = "Keithley Source Meter"
    subtitle = "Keithley Source Meter"
    help_text = """
    <b>Please provide any other important information in other remarks (e.g. toxic samples)</b>
    """

    class Meta(UserDetailsForm.Meta, UserRemarkForm.Meta):
        model = KeithleySourceMeter
        fields = (
            UserDetailsForm.Meta.fields
            + (
                "sample_codes",
                "iv_characterization",
                "resistance_measurement",
                "voltage_range_start",
                "voltage_range_end",
                "current_range_start",
                "current_range_end",
            )
            + UserRemarkForm.Meta.fields
        )

        labels = dict(
            **UserDetailsForm.Meta.labels,
            **UserRemarkForm.Meta.labels,
            sample_codes="Sample Codes",
            iv_characterization="Current–Voltage (I–V) Characterization",
            resistance_measurement="Resistance Measurement",
            voltage_range_start="Voltage Range Start (V)",
            voltage_range_end="Voltage Range End (V)",
            current_range_start="Current Range Start (µA)",
            current_range_end="Current Range End (µA)",
        )

        widgets = dict(
            **UserDetailsForm.Meta.widgets,
            **UserRemarkForm.Meta.widgets,
            sample_codes=forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            iv_characterization=forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            resistance_measurement=forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            voltage_range_start=forms.NumberInput(
                attrs={
                    "class": "form-control",
                }
            ),
            voltage_range_end=forms.NumberInput(
                attrs={
                    "class": "form-control",
                }
            ),
            current_range_start=forms.NumberInput(
                attrs={
                    "class": "form-control",
                }
            ),
            current_range_end=forms.NumberInput(
                attrs={
                    "class": "form-control",
                }
            ),
        )
