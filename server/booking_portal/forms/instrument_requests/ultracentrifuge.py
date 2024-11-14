from booking_portal.models.instrument.requests import Ultracentrifuge
from django import forms

from .base import UserDetailsForm, UserRemarkForm


class UltracentrifugeForm(UserDetailsForm, UserRemarkForm):
    title = "Ultracentrifuge"
    subtitle = "Ultracentrifuge (Optima - XPN-100)"
    help_text = """
        <b>Please provide any other information in other remarks (eg. toxic samples).</b> <br>
        <b>Note: Clean Quartz Cuvettes with utmost care and inform Technical staff before and after the analysis.</b>
    """

    class Meta(UserDetailsForm.Meta, UserRemarkForm.Meta):
        model = Ultracentrifuge

        fields = (
            UserDetailsForm.Meta.fields
            + (
                "sample_codes",
                "slot_duration",
                "rotor_used",
                "solvent",
                "tubes_used",
                "utilization_of_rotor",
                "additional_info",
            )
            + UserRemarkForm.Meta.fields
        )

        labels = dict(
            **UserDetailsForm.Meta.labels,
            **UserRemarkForm.Meta.labels,
            **{
                "sample_codes": "Sample Codes",
                "slot_duration": "Slot Duration(3hr)",
                "rotor_used": "Rotor Used",
                "solvent": "Solvent Used",
                "tubes_used": "Tubes Used",
                "utilization_of_rotor": "Utilization of Rotor & RPM (No. of Hrs)",
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
                "rotor_used": forms.Select(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "solvent": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "tubes_used": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "utilization_of_rotor": forms.TextInput(
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
