from django import forms

from booking_portal.models.instrument.requests import EPR_ESR

from .base import UserDetailsForm, UserRemarkForm


class EPR_ESRForm (UserDetailsForm, UserRemarkForm):
    title = "Electron Paramagnetic Resonance"
    subtitle = "(Bruker - Magnettech ESR5000 Benchtop Spectrometer)"
    help_text = '''
    <b>Note: *Temperature series(LN2 Samples) will be done monthly twice depends on pool of samples.</b>
    <b>Please provide any other information in other remarks (eg. toxic samples) </b>
    '''

    class Meta(UserDetailsForm.Meta, UserRemarkForm.Meta):
        model = EPR_ESR
        fields = UserDetailsForm.Meta.fields + \
            (
                'sample_code',
                'sample_nature',
                'field',
                'temperature_series',
            ) + \
            UserRemarkForm.Meta.fields

        labels = dict(
            ** UserDetailsForm.Meta.labels,
            ** UserRemarkForm.Meta.labels,
            ** {
                'sample_code': 'Sample Codes',
                'sample_nature': 'Nature of Sample',
                'field': 'Field(B) Range(mT)',
                'temperature_series': "RT/Temperature Series *",
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
                'temperature_series': forms.TextInput(attrs={
                    'class': 'form-control',
                }
                ),
            },
        )
