from django import forms

from booking_portal.models.instrument.requests import FluorescenceMicroscope

from .base import UserDetailsForm, UserRemarkForm


class FluorescenceMicroscopeForm(UserDetailsForm, UserRemarkForm):
    title = "Fluorescence Microscope"
    subtitle = "Fluorescence Microscope (Leica - Mateo FL)"
    help_text = """
    Note: When you are using Disposable cuvettes please clean with water only and inform Technical staff before and after the analysis.
    <br><b>Please provide any other important information in other remarks (e.g. toxic samples)</b>
    """

    class Meta(UserDetailsForm.Meta, UserRemarkForm.Meta):
        model = FluorescenceMicroscope
        fields = (
            UserDetailsForm.Meta.fields
            + (
                "sample_description",
                "sample_type",
                "imaging_mode",
            )
            + UserRemarkForm.Meta.fields
        )

        labels = dict(
            **UserDetailsForm.Meta.labels,
            **UserRemarkForm.Meta.labels,
            sample_description="Sample Description",
            sample_type="Sample Origin / Type",
            imaging_mode="Imaging Mode",
        )

        widgets = dict(
            **UserDetailsForm.Meta.widgets,
            **UserRemarkForm.Meta.widgets,
            sample_description=forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            sample_type=forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            imaging_mode=forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
        )
