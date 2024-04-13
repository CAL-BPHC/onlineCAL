from django import forms

from booking_portal.models.instrument.requests import UVSpectrophotometer

from .base import UserDetailsForm, UserRemarkForm


class UVSpectrophotometerForm(UserDetailsForm, UserRemarkForm):
    title = "UV-VIS-NIR Spectrophotometer"
    subtitle = "UV-VIS-NIR Spectrophotometer-Jasco UV 670"
    help_text = '''
    <b>Please provide any other information in other remarks (eg. toxic samples) </b>
    '''

    class Meta(UserDetailsForm.Meta, UserRemarkForm.Meta):
        model = UVSpectrophotometer
        fields = UserDetailsForm.Meta.fields + \
            (
                'sample_code',
                'sample_composition',
                'molecular_weight',
                'analysis_mode',
                'wavelength',
                'ordinate_mode',
            ) + \
            UserRemarkForm.Meta.fields

        labels = dict(
            ** UserDetailsForm.Meta.labels,
            ** UserRemarkForm.Meta.labels,
            ** {
                'sample_code': 'Sample Code',
                'sample_composition': 'Sample Composition',
                'molucular_weight': 'Molecular weight of the sample (if mode of analysis is liquid)',
                'analysis_mode': 'Mode of analysis',
                'wavelength': 'Wavelength range for analysis',
                'ordinate_mode': 'Ordinate Mode %A%T%R',
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
                'sample_composition': forms.TextInput(attrs={
                    'class': 'form-control',
                }
                ),
                'molecular_weight': forms.TextInput(attrs={
                    'class': 'form-control',
                }
                ),
                'analysis_mode': forms.Select(attrs={
                    'class': 'form-control',
                }
                ),
                'wavelength': forms.TextInput(attrs={
                    'class': 'form-control',
                }
                ),
                'ordinate_mode': forms.TextInput(attrs={
                    'class': 'form-control',
                }
                ),
            }
        )
