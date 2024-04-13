from django import forms

from booking_portal.models.instrument.requests import XPS

from .base import UserDetailsForm, UserRemarkForm


class XPSForm(UserDetailsForm, UserRemarkForm):
    title = "XPS-Thermo Scientific K-Alpha"
    subtitle = "XPS-Thermo Scientific K-Alpha"
    help_text = '''
    <b>Please provide any other information in other remarks (eg. toxic samples) </b><br>
        <b>Mention any volatile elements like I, S, Hg</b>
    '''

    class Meta(UserDetailsForm.Meta, UserRemarkForm.Meta):
        model = XPS
        fields = UserDetailsForm.Meta.fields + \
            (
                'sample_name',
                'sample_nature',
                'chemical_composition',
                'sample_property',
                'analysed_elements',
                'scan_details',
            ) + \
            UserRemarkForm.Meta.fields

        labels = dict(
            ** UserDetailsForm.Meta.labels,
            ** UserRemarkForm.Meta.labels,
            ** {
                'sample_name': 'Sample Name',
                'sample_nature': 'Nature of Sample (pellet: 1cm dia with 2-3mm thickness or Thin Film: 1 x 1 cm^2)',
                'chemical_composition': 'Chemical Composition',
                'sample_property': 'Sample Property',
                'analysed_elements': 'Elements to be analysed',
                'scan_details': 'Scan details specification (Expected B.E.)',
            }
        )

        widgets = dict(
            ** UserDetailsForm.Meta.widgets,
            ** UserRemarkForm.Meta.widgets,
            ** {
                'sample_name': forms.TextInput(attrs={
                    'class': 'form-control',
                }
                ),
                'sample_nature': forms.TextInput(attrs={
                    'class': 'form-control',
                }
                ),
                'chemical_composition': forms.TextInput(attrs={
                    'class': 'form-control',
                }
                ),
                'sample_property': forms.Select(attrs={
                    'class': 'form-control',
                }
                ),
                'analysed_elements': forms.TextInput(attrs={
                    'class': 'form-control',
                }
                ),
                'scan_details': forms.TextInput(attrs={
                    'class': 'form-control',
                }
                ),
            }
        )
