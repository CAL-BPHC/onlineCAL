from booking_portal.models.instrument.requests import GC
from django import forms

from .base import UserDetailsForm, UserRemarkForm


class GCForm(UserDetailsForm, UserRemarkForm):
    title = "Gas Chromatography"
    subtitle = "Gas Chromatography (GC) Shimadzu - 2010 PLUS"
    help_text = """
    <b>Note:</b> User is requested to adopt standard techniques for preparation of samples before giving them. <br>
        The sample should be filtered through 0.2 micrometer PTFE filter.
    """

    class Meta(UserDetailsForm.Meta, UserRemarkForm.Meta):
        model = GC
        fields = (
            UserDetailsForm.Meta.fields
            + (
                "sample_code",
                "appearance",
                "no_of_gc_peaks",
                "solvent_solubility",
                "column_details",
                "exp_mol_wt",
                "mp_bp",
                "sample_source",
            )
            + UserRemarkForm.Meta.fields
        )

        labels = dict(
            **UserDetailsForm.Meta.labels,
            **UserRemarkForm.Meta.labels,
            **{
                "sample_code": "Sample Code",
                "appearance": "Color and Appearance",
                "no_of_gc_peaks": "No. of GC Peaks",
                "solvent_solubility": "Solvent Solubility",
                "column_details": "Column Details",
                "exp_mol_wt": "Exp. Mol. Wt.",
                "mp_bp": "MP / BP (C)",
                "sample_source": "Sample Source (Natural/ Synthesis/ Waste)",
            },
        )

        widgets = dict(
            **UserDetailsForm.Meta.widgets,
            **UserRemarkForm.Meta.widgets,
            **{
                "sample_code": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "appearance": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "no_of_gc_peaks": forms.NumberInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "solvent_solubility": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "column_details": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "exp_mol_wt": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "mp_bp": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "sample_source": forms.Select(
                    attrs={
                        "class": "form-control",
                    }
                ),
            },
        )
