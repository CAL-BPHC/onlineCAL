from django import forms

from booking_portal.models.instrument.requests import DigitalPolarimeter

from .base import UserDetailsForm, UserRemarkForm


class DigitalPolarimeterForm(UserDetailsForm, UserRemarkForm):
    title = "Digital Polarimeter"
    subtitle = "Digital Polarimeter (Jasco - P-2000)"
    help_text = '''
        <b>Please provide any other information in other remarks (eg. toxic samples).</b> <br>
        <b>Note: Clean Quartz Cuvettes with utmost care and inform Technical staff before and after the analysis.</b>
    '''

    class Meta(UserDetailsForm.Meta, UserRemarkForm.Meta):
        model = DigitalPolarimeter

        fields = UserDetailsForm.Meta.fields + \
            (
                "sample_codes",
                "slot_duration",
                "filters_used",
                "measurement_type",
                "solvent",
                "cuvette_path_length",
                "additional_info",
            ) + \
            UserRemarkForm.Meta.fields

        labels = dict(
            **UserDetailsForm.Meta.labels,
            **UserRemarkForm.Meta.labels,
            **{
                "sample_codes": "Sample Codes",
                "slot_duration": "Slot Duration(2hr)",
                "filters_used": "Filters Used",
                "measurement_type": "Type of Measurement",
                "solvent": "Solvent Used",
                "cuvette_path_length": "Cuvette Path Length",
                "additional_info": "Any remarks"
            }
        )

        widgets = dict(
            **UserDetailsForm.Meta.widgets,
            **UserRemarkForm.Meta.widgets,
            **{
                "sample_codes": forms.TextInput(attrs={"class": "form-control", }),
                "slot_duration": forms.TextInput(attrs={"class": "form-control", }),
                "filters_used": forms.TextInput(attrs={"class": "form-control", }),
                "measurement_type": forms.TextInput(attrs={"class": "form-control", }),
                "solvent": forms.TextInput(attrs={"class": "form-control", }),
                "cuvette_path_length": forms.TextInput(attrs={"class": "form-control", }),
                "additional_info": forms.TextInput(attrs={"class": "form-control", }),
            }
        )
