from django import forms

from booking_portal.models.instrument.requests import DSC

from .base import UserDetailsForm, UserRemarkForm


class DSCForm(UserDetailsForm, UserRemarkForm):
    title = "Differential Scanning Calorimeter"
    subtitle = "Differential Scanning Calorimeter - Shimadzu DSC-60"
    help_text = '''
    AMOUNT OF SAMPLE: A minimum of 2-5 mg for solids and 10 microlitre for liquids <br>
        <b>Please provide any other information in other remarks (eg. toxic samples) </b>
    '''

    class Meta(UserDetailsForm.Meta, UserRemarkForm.Meta):
        model = DSC
        fields = UserDetailsForm.Meta.fields + \
            ('sample_code',
             'chemical_composition',
             'sample_amount',
             'heating_program',
             'temp_range',
             'atmosphere',
             'heating_rate',
             ) + \
            UserRemarkForm.Meta.fields

        labels = dict(
            ** UserDetailsForm.Meta.labels,
            ** UserRemarkForm.Meta.labels,
            ** {
                'sample_code': 'Sample Code',
                'chemical_composition': 'Chemical Composition',
                'sample_amount': 'Amount of Sample / mg',
                'heating_program': 'Heating Program (dynamic / isothermal)',
                'temp_range': 'Temperature Range (in degree celsius)',
                'atmosphere': 'Atmosphere (N2, Ar, Air)',
                'heating_rate': 'Heating Rate / C min^-1',
            }
        )

        widgets = dict(
            ** UserDetailsForm.Meta.widgets,
            ** UserRemarkForm.Meta.widgets,
            ** {
                'sample_code': forms.TextInput(attrs={
                    'class': 'form-control',
                }
                ),
                'chemical_composition': forms.TextInput(attrs={
                    'class': 'form-control',
                }
                ),
                'sample_amount': forms.TextInput(attrs={
                    'class': 'form-control',
                }
                ),
                'heating_program': forms.Select(attrs={
                    'class': 'form-control',
                }
                ),
                'temp_range': forms.TextInput(attrs={
                    'class': 'form-control',
                }
                ),
                'atmosphere': forms.Select(attrs={
                    'class': 'form-control',
                }
                ),
                'heating_rate': forms.TextInput(attrs={
                    'class': 'form-control',
                }
                ),
            }
        )
