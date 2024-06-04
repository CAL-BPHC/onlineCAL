from django import forms

from booking_portal.models.instrument.requests import DLS

from .base import UserDetailsForm, UserRemarkForm


class DLSForm(UserDetailsForm, UserRemarkForm):
    title = "Dynamic Light Scattering-Particle Analyzer System (DLS)"
    subtitle = "Dynamic Light Scattering-Particle Analyzer System (DLS) - (Antonpaar - Litesizer DLS 700)"
    help_text = '''
        <b>When you are using Disposable cuvettes please clean with water only and inform Technical staff before and
after the analysis.</b>
        <b>Please provide any other information in other remarks (eg. toxic samples).</b> <br>
    '''

    class Meta(UserDetailsForm.Meta, UserRemarkForm.Meta):
        model = DLS

        fields = UserDetailsForm.Meta.fields + \
            (
                "sample_codes",
                "slot_duration",
                "cuvettes",
                "solvent",
                "additional_info",
            ) + \
            UserRemarkForm.Meta.fields

        labels = dict(
            **UserDetailsForm.Meta.labels,
            **UserRemarkForm.Meta.labels,
            **{
                "sample_codes": "Sample Codes",
                "slot_duration": "Slot Duration(3hr)",
                "cuvettes": "Cuvettes",
                "solvent": "Solvent Used",
                "additional_info": "Any other relevant information"
            }
        )

        widgets = dict(
            **UserDetailsForm.Meta.widgets,
            **UserRemarkForm.Meta.widgets,
            **{
                "sample_codes": forms.TextInput(attrs={"class": "form-control", }),
                "slot_duration": forms.TextInput(attrs={"class": "form-control", }),
                "cuvettes": forms.Select(attrs={"class": "form-control", }),
                "solvent": forms.TextInput(attrs={"class": "form-control", }),
                "additional_info": forms.TextInput(attrs={"class": "form-control", }),
            }
        )
