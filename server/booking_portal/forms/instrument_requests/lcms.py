from booking_portal.models.instrument.requests import LCMS
from django import forms

from .base import UserDetailsForm, UserRemarkForm


class LCMSForm(UserDetailsForm, UserRemarkForm):
    title = "Liquid Chromatography - Mass Spectroscopy"
    subtitle = "Liquid Chromatography - Mass Spectroscopy"
    help_text = """
        Note: User is requested to adopt standard technique for preparation of samples before giving them. <br>
        The sample should be filtered through 0.2 μm PTFE filter.
    """

    class Meta(UserDetailsForm.Meta, UserRemarkForm.Meta):
        model = LCMS
        fields = (
            UserDetailsForm.Meta.fields
            + (
                "sample_code",
                "composition",
                "phase",
                "no_of_lc_peaks",
                "solvent_solubility",
                "exact_mass",
                "mass_adducts",
                "analysis_mode",
            )
            + UserRemarkForm.Meta.fields
        )

        labels = dict(
            **UserDetailsForm.Meta.labels,
            **UserRemarkForm.Meta.labels,
            **{
                "sample_code": "Sample Code",
                "composition": "Sample Information / Composition",
                "phase": "Mobile Phase and Column for LC",
                "no_of_lc_peaks": "No. of LC peaks",
                "solvent_solubility": "Solvent Solubility",
                "exact_mass": "Exact Mass",
                "mass_adducts": "Expected Mass Adducts",
                "analysis_mode": "Mode of Analysis (Positive / Negative)",
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
                "composition": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "phase": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "no_of_lc_peaks": forms.NumberInput(
                    attrs={
                        "class": " form-control",
                    }
                ),
                "solvent_solubility": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "exact_mass": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "mass_adducts": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "analysis_mode": forms.Select(
                    attrs={
                        "class": "form-control",
                    }
                ),
            },
        )
