from django import forms

from booking_portal.models.instrument.requests import NanoDrop

from .base import UserDetailsForm, UserRemarkForm


class NanoDropForm(UserDetailsForm, UserRemarkForm):
    title = "NanoDrop"
    subtitle = "NanoDrop"
    help_text = """
    Note: When you are using Disposable cuvettes please clean with water only and inform Technical staff before and after the analysis.
    <br><b>Please provide any other important information in other remarks (e.g. toxic samples)</b>
    """

    class Meta(UserDetailsForm.Meta, UserRemarkForm.Meta):
        model = NanoDrop
        fields = (
            UserDetailsForm.Meta.fields
            + (
                "sample_codes",
                "sample_type",
                "analysis_required",
            )
            + UserRemarkForm.Meta.fields
        )

        labels = dict(
            **UserDetailsForm.Meta.labels,
            **UserRemarkForm.Meta.labels,
            sample_codes="Sample Codes",
            sample_type="Sample Type",
            analysis_required="Analysis Required",
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
            analysis_required=forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
        )
