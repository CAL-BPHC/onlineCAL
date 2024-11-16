from booking_portal.models.instrument.requests import CDSpectrophotometer
from django import forms

from .base import UserDetailsForm, UserRemarkForm


class CDSpectrophotometerForm(UserDetailsForm, UserRemarkForm):
    title = "Circular Dichroism (CD) Spectrophotometer"
    subtitle = "Circular Dichroism (CD) Spectrophotometer, Jasco J-1500"
    help_text = """
    Sample quality required is 2ml <br>
    Sample should be clear and uniform liquid. Blank solution needs to be submitted by the user.<br>
    <b>Please provide any other information in other remarks (eg. toxic samples) </b>
    """

    class Meta(UserDetailsForm.Meta, UserRemarkForm.Meta):
        model = CDSpectrophotometer
        fields = (
            UserDetailsForm.Meta.fields
            + (
                "sample_code",
                "wavelength_scan_start",
                "wavelength_scan_end",
                "wavelength_fixed",
                "temp_range_scan_start",
                "temp_range_scan_end",
                "temp_range_fixed",
                "concentration",
                "cell_path_length",
            )
            + UserRemarkForm.Meta.fields
        )

        labels = dict(
            **UserDetailsForm.Meta.labels,
            **UserRemarkForm.Meta.labels,
            **{
                "sample_code": "Sample Code",
                "wavelength_scan_start": "Wavalength Range - Scan - Start",
                "wavelength_scan_end": "Wavelength Range - Scan - End",
                "wavelength_fixed": "Wavelength Range - Fixed",
                "temp_range_scan_start": "Temperature Range (20-70 C) - Scan - Start",
                "temp_range_scan_end": "Temperature Range (20-70 C) - Scan - End",
                "temp_range_fixed": "Temperature Range (20-70 C) - Fixed",
                "concentration": "Concentration in mg/ml",
                "cell_path_length": "Cell path length 0.1 / 0.2 / 0.5 / 1 cm",
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
                "wavelength_scan_start": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "wavelength_scan_end": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "wavelength_fixed": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "temp_range_scan_start": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "temp_range_scan_end": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "temp_range_fixed": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "concentration": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "cell_path_length": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
            },
        )
