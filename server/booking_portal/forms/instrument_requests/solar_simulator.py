from django import forms

from booking_portal.models.instrument.requests import SolarSimulator

from .base import UserDetailsForm, UserRemarkForm


class SolarSimulatorForm(UserDetailsForm, UserRemarkForm):
    title = "Solar Simulator"
    subtitle = "Solar Simulator"
    help_text = """
    <b>Please provide any other important information in other remarks (e.g. toxic samples)</b>
    """

    class Meta(UserDetailsForm.Meta, UserRemarkForm.Meta):
        model = SolarSimulator
        fields = (
            UserDetailsForm.Meta.fields
            + (
                "sample_codes",
                "measurement_requirement",
                "measurement_condition",
                "light_intensity",
            )
            + UserRemarkForm.Meta.fields
        )

        labels = dict(
            **UserDetailsForm.Meta.labels,
            **UserRemarkForm.Meta.labels,
            sample_codes="Sample Codes",
            measurement_requirement="Measurement Requirement",
            measurement_condition="Measurement Condition",
            light_intensity="Required Light Intensity (mW/cm²)",
        )

        widgets = dict(
            **UserDetailsForm.Meta.widgets,
            **UserRemarkForm.Meta.widgets,
            sample_codes=forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            measurement_requirement=forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            measurement_condition=forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            light_intensity=forms.NumberInput(
                attrs={
                    "class": "form-control",
                }
            ),
        )
