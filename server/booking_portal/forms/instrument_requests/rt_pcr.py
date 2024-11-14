from booking_portal.models.instrument.requests import RT_PCR
from django import forms

from .base import UserDetailsForm, UserRemarkForm


class RT_PCRForm(UserDetailsForm, UserRemarkForm):
    title = "Real Time PCR System"
    subtitle = "Real Time PCR System(RT-PCR) (Bio-Rad - CFX OPUS 96)"
    help_text = """
    <b>Please do not lean on the instrument and inform Technical staff before and after the analysis.</b>
    <b>Please provide any other information in other remarks (eg. toxic samples) </b>
    """

    class Meta(UserDetailsForm.Meta, UserRemarkForm.Meta):
        model = RT_PCR
        fields = (
            UserDetailsForm.Meta.fields
            + ("sample_type", "slot_duration", "fluorophore", "strips_plate")
            + UserRemarkForm.Meta.fields
        )

        labels = dict(
            **UserDetailsForm.Meta.labels,
            **UserRemarkForm.Meta.labels,
            **{
                "sample_type": "Sample Type",
                "slot_duration": "Sample Duration (3hrs)",
                "fluorophore": "Fluorophore Used",
                "strips_plate": "Strips/Plate",
            },
        )

        widgets = dict(
            **UserDetailsForm.Meta.widgets,
            **UserRemarkForm.Meta.widgets,
            **{
                "sample_type": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "slot_duration": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "fluorophore": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "strips_plate": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
            },
        )
