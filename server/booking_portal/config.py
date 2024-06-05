from .forms.instrument_requests import *
from .models.instrument.requests import *

# Important: In case of a database reset, the instruments have to be added
# in the order in which they are mentioned below For eg. first FESEM instrument
#  will be registered on portal then TCSPC and so on
#
# New instruments should be appended at the last of the list

# NOTE: This is a very, very brittle way of doing things. They key for
# `form_template_dict` is the primary key of the 'Instrument' model. An
# alternative method needs to be found.

# NOTE2: An entry for UTM in the Instrument model is inserted as part of
# DB migrations. We can retroactively modify the previous migrations to do
# the same for the other instruments. and probably use clearly defined
# constants as the variable name.

form_template_dict = {
    1: (FESEMForm, FESEM),
    2: (TCSPCForm, TCSPC),
    3: (FTIRForm, FTIR),
    4: (LCMSForm, LCMS),
    5: (RheometerForm, Rheometer),
    6: (AASForm, AAS),
    7: (TGAForm, TGA),
    8: (BETForm, BET),
    9: (CDSpectrophotometerForm, CDSpectrophotometer),
    10: (LSCMForm, LSCM),
    11: (DSCForm, DSC),
    12: (GCForm, GC),
    13: (EDXRFForm, EDXRF),
    14: (HPLCForm, HPLC),
    15: (NMRForm, NMR),
    16: (PXRDForm, PXRD),
    17: (SCXRDForm, SCXRD),
    18: (XPSForm, XPS),
    19: (UVSpectrophotometerForm, UVSpectrophotometer),
    20: (HPLC_FDForm, HPLC_FD),
    21: (UTMForm, UTM),
    22: (SAXSWAXSForm, SAXS_WAXS),
    23: (VSMForm, VSM),
    24: (EPR_ESRForm, EPR_ESR),
    25: (GPCForm, GPC),
    26: (CHNSForm, CHNS),
    27: (RT_PCRForm, RT_PCR),
    28: (QuantachromeForm, Quantachrome),
    29: (DLSForm, DLS),
    30: (BDFACSForm, BDFACS),
    31: (ContactAngleForm, ContactAngle),
    32: (DigitalPolarimeterForm, DigitalPolarimeter),
    33: (Fluorolog3Form, Fluorolog3),
    34: (FluoromaxForm, Fluoromax),
    35: (SpectraFluorimeterForm, SpectraFluorimeter),
    36: (UltracentrifugeForm, Ultracentrifuge)
}

view_application_dict = {model: form
                         for idx, (form, model) in form_template_dict.items()}
