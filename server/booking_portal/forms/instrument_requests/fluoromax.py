from django import forms

from booking_portal.models.instrument.requests import Fluoromax

from .base import UserDetailsForm, UserRemarkForm


class FluoromaxForm(UserDetailsForm, UserRemarkForm):
    title = "Spectrofluometer"
    subtitle = "Spectrofluometer (Horiba - Fluoromax Plus CP))"
    help_text = '''
        <b>Please provide any other information in other remarks (eg. toxic samples).</b> <br>
        <b>Note: Clean Quartz Cuvettes with utmost care and inform Technical staff before and after the analysis.</b>
    '''

    class Meta(UserDetailsForm.Meta, UserRemarkForm.Meta):
        model = Fluoromax

        fields = UserDetailsForm.Meta.fields + \
            (
                "sample_codes",
                "slot_duration",
                "lasers",
                "excitation_emission",
                "sample_type",
                "utilization_of_source",
                "additional_info",
            ) + \
            UserRemarkForm.Meta.fields

        labels = dict(
            **UserDetailsForm.Meta.labels,
            **UserRemarkForm.Meta.labels,
            **{
                "sample_codes": "Sample Codes",
                "slot_duration": "Slot Duration(4hr)",
                "lasers": "Lasers/NIR",
                "excitation_emission": "Excitation/Emission",
                "sample_type": "Type of Sample & solvent used",
                "utilization_of_source" : "Utilization of Source (No. of Hrs)",
                "additional_info": "Any remarks"
            }
        )

        widgets = dict(
            **UserDetailsForm.Meta.widgets,
            **UserRemarkForm.Meta.widgets,
            **{
                "sample_codes": forms.TextInput(attrs={"class": "form-control", }),
                "slot_duration": forms.TextInput(attrs={"class": "form-control", }),
                "lasers": forms.TextInput(attrs={"class": "form-control", }),
                "excitation_emission": forms.TextInput(attrs={"class": "form-control", }),
                "sample_type": forms.TextInput(attrs={"class": "form-control", }),
                "utilization_of_source":forms.TextInput(attrs={"class": "form-control", }),
                "additional_info": forms.TextInput(attrs={"class": "form-control", }),
            }
        )