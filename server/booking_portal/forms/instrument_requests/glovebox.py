from django import forms

from booking_portal.models.instrument.requests import Glovebox

from .base import UserDetailsForm, UserRemarkForm


class GloveboxForm(UserDetailsForm, UserRemarkForm):
    title = "Glovebox"
    subtitle = "Glovebox"
    help_text = """
    <b>Please provide any other important information in other remarks (e.g. toxic samples)</b>
    """

    class Meta(UserDetailsForm.Meta, UserRemarkForm.Meta):
        model = Glovebox
        fields = (
            UserDetailsForm.Meta.fields
            + (
                "sample_type",
                "experiment_type",
            )
            + UserRemarkForm.Meta.fields
        )

        labels = dict(
            **UserDetailsForm.Meta.labels,
            **UserRemarkForm.Meta.labels,
            sample_type="Type of Sample",
            experiment_type="Type of Experiment",
        )

        widgets = dict(
            **UserDetailsForm.Meta.widgets,
            **UserRemarkForm.Meta.widgets,
            sample_type=forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            experiment_type=forms.Textarea(
                attrs={
                    "class": "form-control",
                }
            ),
        )
