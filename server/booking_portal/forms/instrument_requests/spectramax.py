from django import forms

from booking_portal.models.instrument.requests import SpectraMax

from .base import UserDetailsForm, UserRemarkForm


class SpectraMaxForm(UserDetailsForm, UserRemarkForm):
    title = "SpectraMax iD5"
    subtitle = "SpectraMax iD5"
    help_text = """
    Note: When you are using Disposable cuvettes please clean with water only and inform Technical staff before and after the analysis.
    <br><b>Please provide any other important information in other remarks (e.g. toxic samples)</b>
    """

    class Meta(UserDetailsForm.Meta, UserRemarkForm.Meta):
        model = SpectraMax
        fields = (
            UserDetailsForm.Meta.fields
            + (
                "sample_codes",
                "plate_type",
                "read_mode",
                "read_type",
            )
            + UserRemarkForm.Meta.fields
        )

        labels = dict(
            **UserDetailsForm.Meta.labels,
            **UserRemarkForm.Meta.labels,
            sample_codes="Sample Codes",
            plate_type="Plate Type",
            read_mode="Read Mode",
            read_type="Read Type",
        )

        widgets = dict(
            **UserDetailsForm.Meta.widgets,
            **UserRemarkForm.Meta.widgets,
            sample_codes=forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            plate_type=forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            read_mode=forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            read_type=forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
        )
