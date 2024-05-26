from django import forms

from booking_portal.models.instrument.requests import CHNS

from .base import UserDetailsForm, UserRemarkForm


class CHNSForm (UserDetailsForm, UserRemarkForm):
    title = "CHNS ELEMANTAL ANALYSIS"
    subtitle = "CHNS ELEMANTAL ANALYSIS (MAKE-ELEMEMTAR)"
    help_text = '''
    <b>Please provide any other information in other remarks (eg. toxic samples) </b>
    '''

    class Meta(UserDetailsForm.Meta, UserRemarkForm.Meta):
        model = CHNS
        fields = UserDetailsForm.Meta.fields + \
            (
                'sample_code',
                'sample_nature',
                'parameters',
            ) + \
            UserRemarkForm.Meta.fields

        labels = dict(
            ** UserDetailsForm.Meta.labels,
            ** UserRemarkForm.Meta.labels,
            ** {
                'sample_code': 'Sample Codes',
                'sample_nature': 'Sample Nature',
                'parameters': "Parameters",
            },
        )

        widgets = dict(
            ** UserDetailsForm.Meta.widgets,
            ** UserRemarkForm.Meta.widgets,
            ** {
                'sample_code': forms.TextInput(attrs={
                    'class': 'form-control',
                }),
                'sample_nature': forms.Select(attrs={
                    'class': 'form-control',
                }
                ),
                'parameters': forms.TextInput(attrs={
                    'class': 'form-control',
                }
                ),
            },
        )
