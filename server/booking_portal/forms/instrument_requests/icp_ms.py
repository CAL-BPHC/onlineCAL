from booking_portal.models.instrument.requests import ICPMS
from django import forms

from .base import UserDetailsForm, UserRemarkForm


class ICPMSForm(UserDetailsForm, UserRemarkForm):
    title = "Inductively Coupled Plasma-Mass Spectroscopy (ICP-MS)"
    subtitle = "Inductively Coupled Plasma-Mass Spectroscopy (ICP-MS)"
    help_text = """
    <h4><b>Important Notes:</b></h4>
    <p>1. User need to provide acids (Supra pure 5% HNO<sub>3</sub>, 5% HCl, etc.) for sample preparation and acid microwave digestion.</p>
    <p>2. Sample extracted with HF digestion cannot be run on the ICP-MS system.</p>
    <p>3. "Ar" gas should be replaced by the user after 50 sample analysis.</p>
    <p>4. <b>Available Standard solutions:</b> The Elements are: Ag, Al, B, Ba, Bi, Ca, Cd, Co, Cr, Cu, Fe, Ga, In, K, Li, Mg, Mn, Na, Ni, Pb, Sr, Ti, Zn, Hf, Ir, Sb, Sn, Ta, Ti, Zr, Ce, Y, Au, Ir, Os, Pd, Pt, Re, Rh, Ru, As, P, S, Se, Si and Te.</p>

    <h5><b>I. Sample preparation using microwave digestion system (MDS):</b></h5>

    <p>a. Calculate the elements' weight percent (Wt.%) in the sample.</p>
    <p>b. Convert Wt.% concentration to parts per million (PPM).</p>
    <p>c. Calculate Sample Amount Required for Microwave Digestion.</p>
    <p>d. Calculate the concentration of the element after microwave digestion.</p>
    <p>e. Dilute Stock Solution to below 200 ppb for Instrumental Analysis.</p>

    <h5><b>II. Procedure for ICP-MS Analysis:</b></h5>
    <p><b>The requirements for users bringing samples for ICP-MS analysis.</b></p>

    <h6><b>A. Preparation of rinse and blank solutions:</b></h6>
    <p>Bring <b>2.5 litres of 2% nitric acid</b> (HNO<sub>3</sub>) solution to be used for rinsing the system and as a calibration blank. This acid should be trace-metal grade or equivalent purity to avoid contamination. Lower purity acids can be purified using sub-boiling distillation.</p>

    <h6><b>B. Sample Concentration Below 200 ppb:</b></h6>
    <p>This specifies the desired concentration range for the analytes in the samples being introduced into the ICP-MS. Keeping concentrations below 200 ppb (parts per billion) is important for several reasons:</p>
    <p>i. <b>Avoiding Detector Saturation:</b> High concentrations can saturate the detector, leading to inaccurate results and a non-linear response.</p>
    <p>ii. <b>Minimizing Matrix Effects:</b> Lower concentrations generally exhibit fewer matrix effects, where other components in the sample influence the analyte signal.</p>
    <p>iii. <b>Extending Column/Cone Life:</b> Extremely high concentrations of certain elements can degrade the cones of the ICP-MS, requiring more frequent replacement.</p>

    <h6><b>C. Method for Calibration Curve or Linearity Curve:</b></h6>
    <p>The user providing the method for the calibration or linearity curve is essential for quantitative analysis.</p>

    <p><b>Please provide any other important information on a separate sheet (e.g. toxic samples).</b></p>
    """

    class Meta(UserDetailsForm.Meta, UserRemarkForm.Meta):
        model = ICPMS
        fields = (
            UserDetailsForm.Meta.fields
            + (
                "sample_code",
                "sample_state",
                "target_elements_concentration",
            )
            + UserRemarkForm.Meta.fields
        )

        labels = dict(
            **UserDetailsForm.Meta.labels,
            **UserRemarkForm.Meta.labels,
            **{
                "sample_code": "Sample Code",
                "sample_state": "Sample State (Aqueous, Acid extract, etc.)",
                "target_elements_concentration": "Approx. concentration of target elements (Max 200 ppb)",
                "number_of_samples": "Total Number of Samples (No. of Samples + No. of Standards)",
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
                "sample_state": forms.TextInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
                "target_elements_concentration": forms.NumberInput(
                    attrs={
                        "class": "form-control",
                    }
                ),
            },
        )
