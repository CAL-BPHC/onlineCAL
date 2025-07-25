from booking_portal.models.instrument.requests import ICPMS
from django import forms

from .base import UserDetailsForm, UserRemarkForm


class ICPMSForm(UserDetailsForm, UserRemarkForm):
    title = "Inductively Coupled Plasma-Mass Spectroscopy (ICP-MS)"
    subtitle = "Inductively Coupled Plasma-Mass Spectroscopy (ICP-MS)"
    help_text = """
    <h4><b>Important Notes:</b></h4>
    <p>1. User need to provide acids (Supra pure 65% HNO<sub>3</sub>, 5% HCl) for sample preparation and acid microwave digestion.</p>
    <p>2. Sample extracted with HF digestion cannot be run on the ICP-MS system.</p>
    <p>3. "Ar" gas should be replaced by the user after 50 sample analysis.</p>
    <p>4. <b>Available Standard solutions:</b> The Elements are: Ag, Al, B, Ba, Bi, Ca, Cd, Co, Cr, Cu, Fe, Ga, In, K, Li, Mg, Mn, Na, Ni, Pb, Sr, Ti, Zn, Hf, Ir, Sb, Sn, Ta, Ti, Zr, Ce, Y, Au, V, Ir, Os, Pd, Pt, Re, Rh, Ru, As, P, S, Se, Si and Te.</p>

    <h4><b>I. Sample preparation using microwave digestion system (MDS):</b></h4>

    <h5><b>1. Weighing and Acid (65% supra pure HNO<sub>3</sub>) addition:</b></h5>
    <p>a. Weigh out 5 mg to 10 mg of the sample and transfer it to a microwave digestion vessel.</p>
    <p>b. In a fume hood, carefully add 5 mL to 10 mL of 65% supra pure HNO<sub>3</sub> to the vessel.</p>
    <p>c. For highly reactive or unknown samples, a Pre-digestion step is recommended. Allow the mixture to stand in an open, unsealed vessel for at least 15 minutes or until any visible reaction subsides.</p>

    <h5><b>2. Digestion:</b></h5>
    <p>a. Provide the target digestion temperature based on the specific sample decomposition requirements.</p>
    <p>b. Cap the digestion vessel.</p>
    <p>c. Place the vessel in the microwave system, ensuring the appropriate connections for temperature and pressure sensors are made.</p>
    <p>d. Start the digestion program.</p>

    <h5><b>3. Cooling and depressurization:</b></h5>
    <p>a. When the digestion is complete, allow the tubes to cool undisturbed for a minimum of 30 minutes before removing them from the turntable or opening the vessels. Cooling can be accelerated using internal or external cooling devices.</p>
    <p>b. In a fume hood and using appropriate personal protective equipment (gloves, lab coat, eye protection), carefully open each vessel. Any sample or volume lost during this step will compromise the results.</p>
    <p>c. Rotate the cap slowly using the torque tool, with the vent hole pointing away from you.</p>
    <p>d. You may need to release the pressure slowly by loosening the cap multiple times.</p>

    <h5><b>4. Transfer and check digestion:</b></h5>
    <p>a. Transfer the contents of each vessel into appropriately labeled centrifuge tubes.</p>
    <p>b. Check all samples for complete digestion. If the solution is not clear and homogeneous, repeat the digestion process.</p>

    <h5><b>5. 2% HNO<sub>3</sub> Preparation (2.5 Litters of 2% Nitric Acid):</b></h5>
    <p>a. Use Mili-Q water (ultrapure water) from CALAB-1 for preparing the 2% HNO<sub>3</sub> solution is vital to prevent contamination. High-purity water is essential for trace element work.</p>
    <p><b>Note:</b> Take the 50ml of 65% supra pure HNO<sub>3</sub> and add into 2.5litters of Mili-Q water.</p>
    <p>b. Using 2% HNO<sub>3</sub> for sample dilution: it helps keep the analytes in solution, minimizes matrix effects during ICP-MS analysis, and provides a consistent matrix for calibration standards.</p>

    <h5><b>5. Calculation and dilution:</b></h5>
    <p>a. Calculate the concentration of the digested sample.</p>
    <p>b. Dilute the Sample Concentration Below 200 ppb.</p>
    <p>c. Use 15 mL centrifuge tubes for dilution, ensuring you bring your own tubes for this step.</p>
    <p>d. Dilute the digested sample using the 2% HNO<sub>3</sub> solution.</p>
    <p>e. Makeup Volume(10ml): Making each dilution up to 10ml in centrifuge tubes provides a consistent volume for analysis.</p>
    <p>f. Filtering (0.22 um): Filtering the diluted sample solution using a 0.22 um filter is crucial. This removes any particulate matter that could clog the ICP-MS nebulizer or torch, leading to signal instability or instrument damage.</p>

    <h5><b>6. Cleaning of microwave digestion vessel:</b></h5>
    <p>a. Rinse each vessel thoroughly with deionized water.</p>
    <p>b. Soak each vessel in a 2% nitric acid solution for 10-15 minutes.</p>

    <h4><b>II. Procedure for ICP-MS Analysis:</b></h4>
    <p><b>The requirements for users bringing samples for ICP-MS analysis.</b></p>

    <h5><b>A. Preparation of rinse and blank solutions:</b></h5>
    <p><b>2.5 Litters of 2% Nitric Acid:</b><br>
    Bring 2.5 litters of 2% nitric acid (HNO₃) solution to be used for rinsing the system and as a calibration blank. This acid should be trace-metal grade or equivalent purity to avoid contamination. Lower purity acids can be purified using sub-boiling distillation.</p>

    <h5><b>B. Sample Concentration Below 200 ppb:</b></h5>
    <p>This specifies the desired concentration range for the analytes in the samples being introduced into the ICP-MS. Keeping concentrations below 200 ppb (parts per billion) is important for several reasons:</p>
    <p>i. <b>Avoiding Detector Saturation:</b> High concentrations can saturate the detector, leading to inaccurate results and a non-linear response.</p>
    <p>ii. <b>Minimizing Matrix Effects:</b> Lower concentrations generally exhibit fewer matrix effects, where other components in the sample influence the analyte signal.</p>
    <p>iii. <b>Extending Column/Cone Life:</b> Extremely high concentrations of certain elements can degrade the cones of the ICP-MS, requiring more frequent replacement.</p>

    <h5><b>C. Method for Calibration Curve or Linearity Curve:</b></h5>
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
