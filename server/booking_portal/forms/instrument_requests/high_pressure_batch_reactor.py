from django import forms

from booking_portal.models.instrument.requests import HighPressureBatchReactor

from .base import UserDetailsForm, UserRemarkForm


class HighPressureBatchReactorForm(UserDetailsForm, UserRemarkForm):
    title = "High Pressure Batch Reactor"
    subtitle = "High Pressure Batch Reactor"
    help_text = """
    Note: When you are using Disposable cuvettes please clean with water only and inform Technical staff before and after the analysis.
    <br><b>Please provide any other important information in other remarks (e.g. toxic samples)</b>
    """

    class Meta(UserDetailsForm.Meta, UserRemarkForm.Meta):
        model = HighPressureBatchReactor
        fields = (
            UserDetailsForm.Meta.fields
            + (
                "sample_codes",
                "cuvettes",
                "solvent",
            )
            + UserRemarkForm.Meta.fields
        )

        labels = dict(
            **UserDetailsForm.Meta.labels,
            **UserRemarkForm.Meta.labels,
            sample_codes="Sample Codes",
            cuvettes="Cuvettes",
            solvent="Solvent Used",
        )

        widgets = dict(
            **UserDetailsForm.Meta.widgets,
            **UserRemarkForm.Meta.widgets,
            sample_codes=forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            cuvettes=forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            solvent=forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
        )
