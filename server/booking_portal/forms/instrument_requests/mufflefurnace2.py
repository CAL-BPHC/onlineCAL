from django import forms

from booking_portal.models.instrument.requests import TubularMuffleFurnace

from .base import UserDetailsForm, UserRemarkForm


class MuffleFurnace2Form(UserDetailsForm, UserRemarkForm):
    title = "Muffle Furnace 2"
    subtitle = "Muffle Furnace 2"
    help_text = """
    <b>Note:</b>
    <p>1. User should inform to the CAL technical staff before start the furnace</p>
    <p>2. Make sure Exhaust should be ON before start your experiment and student should be switch OFF exhaust after complete your experiment.</p>
    <p>3. Student should inform to CAL technical staff if any toxic material using in furnace.</p>
    """

    class Meta(UserDetailsForm.Meta, UserRemarkForm.Meta):
        model = TubularMuffleFurnace
        fields = (
            UserDetailsForm.Meta.fields
            + (
                "sample_code",
                "sample_nature",
                "temperature",
                "quantity",
            )
            + UserRemarkForm.Meta.fields
        )

        labels = dict(
            **UserDetailsForm.Meta.labels,
            **UserRemarkForm.Meta.labels,
            **{
                "sample_code": "Sample Code",
                "sample_nature": "Sample Nature",
                "temperature": "Temperature (°C)",
                "quantity": "Quantity (gms)",
            },
        )

        widgets = dict(
            **UserDetailsForm.Meta.widgets,
            **UserRemarkForm.Meta.widgets,
            **{
                "sample_code": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "sample_nature": forms.Select(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "temperature": forms.NumberInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "quantity": forms.NumberInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
            },
        )
