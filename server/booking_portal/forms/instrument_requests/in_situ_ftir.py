from django import forms

from booking_portal.models.instrument.requests import InSituFTIR

from .base import UserDetailsForm, UserRemarkForm


class InSituFTIRForm(UserDetailsForm, UserRemarkForm):
    title = "In-situ Fourier Transform Infrared Spectrometer"
    subtitle = "In-situ Fourier Transform Infrared Spectrometer (FTIR) - PerkinElmer"
    help_text = """
    Note: the minimum amount of the sample should be 2 mg.
    <br><b>Please provide any other important information in other remarks (e.g. toxic samples)</b>
    """

    class Meta(UserDetailsForm.Meta, UserRemarkForm.Meta):
        model = InSituFTIR
        fields = (
            UserDetailsForm.Meta.fields
            + (
                "sample_codes",
                "composition",
                "state",
                "solvent",
            )
            + UserRemarkForm.Meta.fields
        )

        labels = dict(
            **UserDetailsForm.Meta.labels,
            **UserRemarkForm.Meta.labels,
            sample_codes="Sample Codes",
            composition="Composition",
            state="Solid / Liquid",
            solvent="Solvent Used (if any)",
        )

        widgets = dict(
            **UserDetailsForm.Meta.widgets,
            **UserRemarkForm.Meta.widgets,
            sample_codes=forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            composition=forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            state=forms.Select(
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
