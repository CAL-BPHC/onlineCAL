from django import forms

from booking_portal.models.instrument.requests import NMR

from .base import UserDetailsForm, UserRemarkForm


class NMRForm(UserDetailsForm, UserRemarkForm):
    title = "Nuclear Magnetic Resonance (NMR)"
    subtitle = "Nuclear Magnetic Resonance (NMR) Bruker - AV NEO 400MHz"
    help_text = '''
    <b>Please provide any other information in other remarks (eg. toxic samples) </b>
    '''

    class Meta(UserDetailsForm.Meta, UserRemarkForm.Meta):
        model = NMR
        fields = UserDetailsForm.Meta.fields + \
            (
                'sample_code',
                'sample_nature',
                'quantity',
                'solvent',
                'analysis',
                'experiment',
                'spectral_range',
            ) + \
            UserRemarkForm.Meta.fields

        labels = dict(
            ** UserDetailsForm.Meta.labels,
            ** UserRemarkForm.Meta.labels,
            ** {
                'sample_code': 'Sample Code',
                'sample_nature': 'Nature of Sample (Solid or Liquid)',
                'quantity': 'Quantity (in mg)',
                'solvent': 'Solvent for NMR',
                'analysis': 'NMR Analysis (Nuclei)',
                'experiment': '2D-NMR Experiment (if any)',
                'spectral_range': 'Plotting spectral range in ppm (if any)',
            }
        )

        UserDetailsForm.Meta.widgets.update(

        )
        widgets = dict(
            ** UserDetailsForm.Meta.widgets,
            ** UserRemarkForm.Meta.widgets,
            ** {
                'sample_code': forms.TextInput(attrs={
                    'class': 'form-control',
                }
                ),
                'sample_nature': forms.Select(attrs={
                    'class': 'form-control',
                }
                ),
                'quantity': forms.TextInput(attrs={
                    'class': 'form-control',
                }
                ),
                'solvent': forms.TextInput(attrs={
                    'class': 'form-control',
                }
                ),
                'analysis': forms.TextInput(attrs={
                    'class': 'form-control',
                }
                ),
                'experiment': forms.TextInput(attrs={
                    'class': 'form-control',
                }
                ),
                'spectral_range': forms.TextInput(attrs={
                    'class': 'form-control',
                }
                ),
            }
        )
