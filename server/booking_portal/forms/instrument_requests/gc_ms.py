from django import forms

from booking_portal.models.instrument.requests import GCMS

from .base import UserDetailsForm, UserRemarkForm


class GCMSForm(UserDetailsForm, UserRemarkForm):
    title = "Gas Chromatography Mass Spectrometry with ALS (GC-MS)"
    subtitle = "Gas Chromatography Mass Spectrometry with ALS (GC-MS) - (Agilent GC/TQ)"
    help_text = """
    <b>Please provide any other important information in other remarks (e.g. toxic samples)</b>
    """

    class Meta(UserDetailsForm.Meta, UserRemarkForm.Meta):
        model = GCMS
        fields = (
            UserDetailsForm.Meta.fields
            + (
                "sample_codes",
                "required_gas",
                "required_column",
                "mol_wt_formula",
                "required_detector",
            )
            + UserRemarkForm.Meta.fields
        )

        labels = dict(
            **UserDetailsForm.Meta.labels,
            **UserRemarkForm.Meta.labels,
            sample_codes="Sample Codes",
            required_gas="Required Gas",
            required_column="Required Column",
            mol_wt_formula="Molecular Weight and Molecular Formula",
            required_detector="Required Detector",
        )

        widgets = dict(
            **UserDetailsForm.Meta.widgets,
            **UserRemarkForm.Meta.widgets,
            sample_codes=forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            required_gas=forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            required_column=forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            mol_wt_formula=forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            required_detector=forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
        )
