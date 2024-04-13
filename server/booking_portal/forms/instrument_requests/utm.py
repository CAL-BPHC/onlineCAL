"""Universal Testing Machine"""

from django import forms

from booking_portal.models.instrument.requests import UTM

from .base import UserDetailsForm, UserRemarkForm

__author__ = "Abhijeet Viswa"
__license__ = "MIT"


class UTMForm(UserDetailsForm, UserRemarkForm):
    title = "Universal Testing Machine"
    subtitle = "Universal Testing Machine"
    help_text = '''
    <b>Please provide any other information in other remarks (eg: additional temperature details)</b>
    '''

    class Meta(UserDetailsForm.Meta, UserRemarkForm.Meta):
        model = UTM
        fields = UserDetailsForm.Meta.fields + \
            (
                'material',
                'test_type',
                'test_speed',
                'temperature',
            ) + \
            UserRemarkForm.Meta.fields

        labels = dict(
            **UserDetailsForm.Meta.labels,
            **UserRemarkForm.Meta.labels,
            **{
                'material': 'Sample Material',
                'test_type': 'Test Type',
                'test_speed': 'Test Speed (mm/min or 1/s)',
                'temperature': 'Temperature',
            }
        )

        widgets = dict(
            **UserDetailsForm.Meta.widgets,
            **UserRemarkForm.Meta.widgets,
            **{
                'material': forms.TextInput(attrs={
                    'class': 'form-control',
                }
                ),
                'test_type': forms.Select(attrs={
                    'class': 'form-control',
                }
                ),
                'test_speed': forms.NumberInput(attrs={
                    'class': 'form-control',
                }
                ),
                'temperature': forms.NumberInput(attrs={
                    'class': 'form-control',
                }
                ),
            }
        )
