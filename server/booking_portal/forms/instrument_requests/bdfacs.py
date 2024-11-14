from booking_portal.models.instrument.requests import BDFACS
from django import forms

from .base import UserDetailsForm, UserRemarkForm


class BDFACSForm(UserDetailsForm, UserRemarkForm):
    title = "Cell Sorter"
    subtitle = "Cell Sorter (BD-Fluorescence Associated Cell Sorter - Aria-III)"
    help_text = """
        <b>Please provide any other information in other remarks (eg. toxic samples).</b> <br>
        <b>Please maintain utmost cleanliness while pouring the Sheath Fluid or when cleaning of the waste tank and
inform Technical staff before and after the analysis.</b>
    """

    class Meta(UserDetailsForm.Meta, UserRemarkForm.Meta):
        model = BDFACS

        fields = (
            UserDetailsForm.Meta.fields
            + (
                "sample_codes",
                "slot_duration",
                "lasers",
                "excitation_emission",
                "analysis_cell_sorting",
                "additional_info",
            )
            + UserRemarkForm.Meta.fields
        )

        labels = dict(
            **UserDetailsForm.Meta.labels,
            **UserRemarkForm.Meta.labels,
            **{
                "sample_codes": "Sample Codes",
                "slot_duration": "Slot Duration(4hr)",
                "lasers": "Lasers",
                "excitation_emission": "Excitation / Emission",
                "analysis_cell_sorting": "Analysis / Cell Sorting",
                "additional_info": "Any remarks",
            },
        )

        widgets = dict(
            **UserDetailsForm.Meta.widgets,
            **UserRemarkForm.Meta.widgets,
            **{
                "sample_codes": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "slot_duration": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "lasers": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "excitation_emission": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "analysis_cell_sorting": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "additional_info": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
            },
        )
