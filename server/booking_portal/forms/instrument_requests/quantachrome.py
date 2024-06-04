from django import forms

from booking_portal.models.instrument.requests import Quantachrome

from .base import UserDetailsForm, UserRemarkForm


class QuantachromeForm (UserDetailsForm, UserRemarkForm):
    title = "Quantachrome(Anton Paar), autosorb iQ"
    subtitle = "Quantachrome (Anton Paar), autosorb iQ"
    help_text = '''
    <b>Please provide any other information in other remarks (eg. toxic samples) </b>
    '''

    class Meta(UserDetailsForm.Meta, UserRemarkForm.Meta):
        model = Quantachrome
        fields = UserDetailsForm.Meta.fields + \
            (
                'sample_code',
                'pretreatment_conditions',
                'precautions',
                "adsorption",
                "surface_area_pore_size"
            ) + \
            UserRemarkForm.Meta.fields

        labels = dict(
            ** UserDetailsForm.Meta.labels,
            ** UserRemarkForm.Meta.labels,
            ** {
                'sample_code': 'Sample Codes',
                'pretreatment_conditions': "Pretreatment conditions",
                'precautions': "Precautions to be taken",
                "adsorption": "N2/CO2/Vapor Adsorption",
                "surface_area_pore_size": "Specific surface area / surface area and pore size analysis to be required"
            },
        )

        widgets = dict(
            ** UserDetailsForm.Meta.widgets,
            ** UserRemarkForm.Meta.widgets,
            ** {
                'sample_code': forms.TextInput(attrs={
                    'class': 'form-control',
                }),
                'pretreatment_conditions': forms.TextInput(attrs={
                    'class': 'form-control',
                }
                ),
                'precautions': forms.TextInput(attrs={
                    'class': 'form-control',
                }
                ),
                'adsorption': forms.TextInput(attrs={
                    'class': 'form-control',
                }
                ),
                'surface_area_pore_size': forms.TextInput(attrs={
                    'class': 'form-control',
                }
                ),
            },
        )
