from booking_portal.models.instrument.requests import SAXS_WAXS
from django import forms

from .base import UserDetailsForm, UserRemarkForm


class SAXSWAXSForm(UserDetailsForm, UserRemarkForm):
    title = "SAXS/WAXS"
    subtitle = "Small Angle X ray Scattering"

    help_text = """
    <b>Please provide any other information in other remarks (eg. toxic samples) </b>
    """

    class Meta(UserDetailsForm.Meta, UserRemarkForm.Meta):
        model = SAXS_WAXS
        fields = (
            UserDetailsForm.Meta.fields
            + ("sample_code", "nature_of_samples")
            + UserRemarkForm.Meta.fields
        )

        labels = dict(
            **UserDetailsForm.Meta.labels,
            **UserRemarkForm.Meta.labels,
            **{"sample_code": "Sample Code", "nature_of_samples": "Nature of samples"},
        )

        widgets = dict(
            **UserDetailsForm.Meta.widgets,
            **UserRemarkForm.Meta.widgets,
            **{
                "sample_code": forms.TextInput(attrs={"class": "form-control"}),
                "nature_of_samples": forms.Select(attrs={"class": "form-control"}),
            },
        )
