from django import forms

from booking_portal.models.instrument.requests import FESEM

from .base import UserDetailsForm, UserRemarkForm


class FESEMForm (UserDetailsForm, UserRemarkForm):
    title = "Field Emission Scanning Electron Microscope"
    subtitle = "Field Emission Scanning Electron Microscope"
    help_text = """
    <b>Note:</b>
    <p>1. Morning slots (9.30AM to 1.00PM): Submit samples at 9.00AM.</p>
    <p>2. Afternoon slots (2.00PM to 5.00PM): Submit samples at 12.00PM.</p>
    <p>3. Evening slots (5.00PM to 8.00PM): Submit samples at 3.00PM.</p>
    <p>4. Maximum number of samples per slot is 3.</p>
    <p>5. Make sure to choose the right mode while booking the instrument.</p>
    """

    class Meta(UserDetailsForm.Meta, UserRemarkForm.Meta):
        model = FESEM
        fields = UserDetailsForm.Meta.fields + \
            (
                'sample_code',
                'sample_nature',
                'analysis_nature',
                'sputter_required',
            ) + \
            UserRemarkForm.Meta.fields

        labels = dict(
            ** UserDetailsForm.Meta.labels,
            ** UserRemarkForm.Meta.labels,
            ** {
                'sample_code': 'Sample Code',
                'sample_nature': 'Nature of Sample',
                'analysis_nature': 'Nature of Analysis (SEM, EDX, STEM etc.)',
                'sputter_required': 'Sputter coating required',
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
                'analysis_nature': forms.TextInput(attrs={
                    'class': 'form-control',
                }
                ),
                'sputter_required': forms.Select(attrs={
                    'class': 'form-control',
                }
                ),
            },
        )
