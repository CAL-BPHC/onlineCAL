from django import forms

from booking_portal.models.instrument.requests import VSM

from .base import UserDetailsForm, UserRemarkForm


class VSMForm (UserDetailsForm, UserRemarkForm):
    title = "Vibrating Sample Magnetometer"
    subtitle = "(Microsense LLC - EZ7)"
    help_text = '''
    <b>Please provide any other information in other remarks (eg. toxic samples) </b>
    '''

    class Meta(UserDetailsForm.Meta, UserRemarkForm.Meta):
        model = VSM
        fields = UserDetailsForm.Meta.fields + \
            (
                'sample_code',
                'sample_nature',
                'field',
                'step_size',
            ) + \
            UserRemarkForm.Meta.fields

        labels = dict(
            ** UserDetailsForm.Meta.labels,
            ** UserRemarkForm.Meta.labels,
            ** {
                'sample_code': 'Sample Codes',
                'sample_nature': 'Nature of Sample',
                'field': 'Field(B) Range(Oe)',
                'step_size': 'Step Size & Hold Time(secs)',
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
                'field': forms.TextInput(attrs={
                    'class': 'form-control',
                }
                ),
                'step_size': forms.TextInput(attrs={
                    'class': 'form-control',
                }
                ),
            },
        )
