from booking_portal.models.instrument.requests import ICPMS
from django import forms

from .base import UserDetailsForm, UserRemarkForm


class ICPMSForm(UserDetailsForm, UserRemarkForm):
    title = "Inductively Coupled Plasma-Mass Spectroscopy (ICP-MS)"
    subtitle = "Inductively Coupled Plasma-Mass Spectroscopy (ICP-MS)"
    help_text = """
    <b>Note:</b>
    <p>1. Users need to provide acids (Supra pure 5% HNO<sub>3</sub>, 5% HCl, 5% H2SO<sub>4</sub>, etc.) for sample preparation and acid micro digestion.</p>
    <p>2. Sample extracted with HF digestion cannot be run on the ICP-MS system.</p>
    <p>3. Acid micro digestion is mandatory for samples with high organic matter content.</p>
    <p>4. CAL will not under any circumstances store samples after analysis.</p>
    <p>5. Please specify the nature of your sample if it contains any toxic/ flammable/ hazardous/ explosive component. If the sample causes any harm at any instance of the analysis, it will be the responsibility of the user to suitably compensate CAL for the same.</p>
    <p>6. Samples should not be Carcinogenic.</p>
    <p>7. Providing accurate details of the samples is mandatory.</p>
    <p>8. Samples should be properly labeled.</p>
    <p>9. Relevant standards for calibration should be provided.</p>
    <p>10. At least 10-15 ml must be provided for each sample.</p>
    <p>11. "Ar" gas should be replaced by the user after 50 sample analyses.</p>
    """

    class Meta(UserDetailsForm.Meta, UserRemarkForm.Meta):
        model = ICPMS
        fields = (
            UserDetailsForm.Meta.fields
            + (
                "elements",
                "sample_code",
                "sample_state",
                "digestion_carried_out",
                "target_elements_concentration",
                "sample_filtered",
                "calibration_solution_concentration",
                "method",
            )
            + UserRemarkForm.Meta.fields
        )

        labels = dict(
            **UserDetailsForm.Meta.labels,
            **UserRemarkForm.Meta.labels,
            **{
                "elements": """Details of analysis required (List of Expected Elements);
                Available Standard (Multi-standard) elements are: Ag, Al, B, Ba, Bi, Ca, Cd, Co, Cr, Cu, Fe, Ga, In, K, Li, Mg, Mn, Na, Ni, Pb, Sr, Ti, Zn, Hf, Ir, Sb, Sn, Ta, Ti, Zr, Ce, Y, Au.""",
                "sample_code": "Sample Code",
                "sample_state": "Sample State (Aqueous, Acid extract, etc.)",
                "digestion_carried_out": "For samples containing organic matter, was digestion carried out?",
                "target_elements_concentration": "Approx. concentration of target elements (Max 1000 ppb)",
                "sample_filtered": "Has sample been filtered through 0.22 μ filter?",
                "calibration_solution_concentration": "Expected concentration for preparing calibration solution (Max 1000 ppb)",
                "method": "Method Available",
            },
        )

        widgets = dict(
            **UserDetailsForm.Meta.widgets,
            **UserRemarkForm.Meta.widgets,
            **{
                "elements": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "sample_code": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "sample_state": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "digestion_carried_out": forms.Select(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "target_elements_concentration": forms.NumberInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "sample_filtered": forms.Select(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "calibration_solution_concentration": forms.NumberInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "method": forms.Select(
                    attrs={
                        "class": "form-control",
                    }
                ),
            },
        )
