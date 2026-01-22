from booking_portal.models.instrument.requests import ConfocalRamanSpectrometer
from django import forms

from .base import UserDetailsForm, UserRemarkForm


class ConfocalRamanSpectrometerForm(UserDetailsForm, UserRemarkForm):
    title = "Confocal Raman Spectrometer, OXFORD, WITec Model: Alpha300R"
    subtitle = "Confocal Raman Spectrometer"
    help_text = """Note: Make sure to choose the right mode while booking the instrument.
    <br><b>Please provide any other important information in other remarks (e.g. toxic samples)</b>
    """

    class Meta(UserDetailsForm.Meta, UserRemarkForm.Meta):
        model = ConfocalRamanSpectrometer
        fields = (
            UserDetailsForm.Meta.fields
            + (
                "sample_code",
                "sample_nature",
                "scan_range_start",
                "scan_range_end",
                "wavelength",
            )
            + UserRemarkForm.Meta.fields
        )

        labels = dict(
            **UserDetailsForm.Meta.labels,
            **UserRemarkForm.Meta.labels,
            **{
                "sample_code": "Sample Code",
                "sample_nature": "Powder or Film",
                "scan_range_start": "Preferred Scan Range Start (cm⁻¹/nm)",
                "scan_range_end": "Preferred Scan Range End (cm⁻¹/nm)",
                "wavelength": "Wavelength of the laser to be used (nm)",
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
                "sample_nature": forms.Select(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "scan_range_start": forms.NumberInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "scan_range_end": forms.NumberInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "wavelength": forms.NumberInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
            },
        )
