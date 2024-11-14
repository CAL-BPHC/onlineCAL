from booking_portal.models.instrument.requests import FreezeDryer
from django import forms

from .base import UserDetailsForm, UserRemarkForm


class FreezeDryerForm(UserDetailsForm, UserRemarkForm):
    title = "Freeze Dryer"
    subtitle = "Freeze Dryer"
    help_text = """
      <b>Note:</b> User is requested to adopt standard technique for preparation of samples before giving them.
      <p>1) Water content as to be as minimum as possible.</p>
      <p>2) The sample should be well frozen at -80C.</p>
      <p>3) The students should not turn ON the vacuum in the absence of the CAL technical staff.</p>
    """

    class Meta(UserDetailsForm.Meta, UserRemarkForm.Meta):
        model = FreezeDryer
        fields = (
            UserDetailsForm.Meta.fields
            + (
                "sample_code",
                "solvent",
                "freezing_point",
                "quantity",
            )
            + UserRemarkForm.Meta.fields
        )

        labels = dict(
            **UserDetailsForm.Meta.labels,
            **UserRemarkForm.Meta.labels,
            **{
                "sample_code": "Sample Code",
                "solvent": "Solvent",
                "freezing_point": "Freezing Point",
                "quantity": "Quantity (ml)",
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
                "solvent": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "freezing_point": forms.TextInput(
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
