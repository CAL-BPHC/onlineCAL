import calendar

from django.db import models


class UserDetail(models.Model):
    user_name = models.ForeignKey('Student', on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=10)
    date = models.DateField()
    time = models.TimeField()
    duration = models.CharField(max_length=75)
    sup_name = models.ForeignKey('Faculty', on_delete=models.CASCADE)
    sup_dept = models.CharField(max_length=75)
    number_of_samples = models.IntegerField()
    sample_from_outside = models.CharField(max_length=3, choices=[('Yes', 'Yes'),
                                                                  ('No', 'No')])
    origin_of_sample = models.CharField(max_length=75)
    req_discussed = models.CharField(max_length=3, choices=[('Yes', 'Yes'),
                                                            ('No', 'No')])

    def __str__(self):
        return "UserDetail: {} {} {} - {}".format(
            str(self.date.day),
            calendar.month_name[self.date.month],
            str(self.date.year),
            str(self.time)
        )

    class Meta:
        verbose_name = 'User Detail'
        verbose_name_plural = 'User Details'


class UserRemark(models.Model):
    userremark_id = models.AutoField(primary_key=True)
    student_remarks = models.CharField(max_length=250, blank=True, null=True)
    faculty_remarks = models.CharField(max_length=250, blank=True, null=True)
    lab_assistant_remarks = models.CharField(
        max_length=250, blank=True, null=True)

    class Meta:
        verbose_name = "User Remark"
        verbose_name_plural = "User Remarks"


class FESEM(UserDetail, UserRemark):
    sample_code = models.CharField(max_length=75)
    sample_nature = models.CharField(max_length=15, choices=[
        ('Metal', 'Metal'),
        ('Film', 'Film'),
        ('Crystal', 'Crystal'),
        ('Powder', 'Powder'),
        ('Biological',
         'Biological'),
        ('Ceramic', 'Ceramic'),
        ('Tissue', 'Tissue'),
        ('Others', 'Others'),
    ])
    analysis_nature = models.CharField(max_length=75)
    sputter_required = models.CharField(max_length=3, choices=[
        ('Yes', 'Yes'),
        ('No', 'No'),
    ])

    def __str__(self):
        return "{} : {} {} {}".format(
            "FESEM",
            str(self.date.day),
            calendar.month_name[self.date.month],
            str(self.date.year)
        )

    class Meta:
        verbose_name = 'FESEM'
        verbose_name_plural = 'FESEM'


class TCSPC(UserDetail, UserRemark):
    sample_code = models.CharField(max_length=75)
    sample_nature = models.CharField(max_length=15, choices=[
        ('Metal', 'Metal'),
        ('Film', 'Film'),
        ('Crystal', 'Crystal'),
        ('Powder', 'Powder'),
        ('Biological',
         'Biological'),
        ('Ceramic', 'Ceramic'),
        ('Tissue', 'Tissue'),
        ('Others', 'Others'),
    ])
    chemical_composition = models.CharField(max_length=75)

    def __str__(self):
        return "{} : {} {} {}".format(
            "TCSPC",
            str(self.date.day),
            calendar.month_name[self.date.month],
            str(self.date.year)
        )

    class Meta:
        verbose_name = 'TCSPC'
        verbose_name_plural = 'TCSPC'


class FTIR(UserDetail, UserRemark):
    sample_code = models.CharField(max_length=75)
    composition = models.CharField(max_length=75)
    state = models.CharField(max_length=10, choices=[
        ('Solid', 'Solid'),
        ('Liquid', 'Liquid'),
    ])
    solvent = models.CharField(max_length=75)

    def __str__(self):
        return "{} : {} {} {}".format(
            "FTIR",
            str(self.date.day),
            calendar.month_name[self.date.month],
            str(self.date.year)
        )

    class Meta:
        verbose_name = 'FTIR'
        verbose_name_plural = 'FTIR'


class LCMS(UserDetail, UserRemark):
    sample_code = models.CharField(max_length=75)
    composition = models.CharField(max_length=75)
    phase = models.CharField(max_length=75)
    no_of_lc_peaks = models.IntegerField()
    solvent_solubility = models.CharField(max_length=75)
    exact_mass = models.CharField(max_length=75)
    mass_adducts = models.CharField(max_length=75)
    analysis_mode = models.CharField(max_length=10, choices=[
        ('Positive', 'Positive'),
        ('Negative', 'Negative'),
    ])

    def __str__(self):
        return "{} : {} {} {}".format(
            "LCMS",
            str(self.date.day),
            calendar.month_name[self.date.month],
            str(self.date.year)
        )

    class Meta:
        verbose_name = 'LCMS'
        verbose_name_plural = 'LCMS'


class Rheometer(UserDetail, UserRemark):
    sample_code = models.CharField(max_length=75)
    ingredient_details = models.CharField(max_length=75)
    physical_characteristics = models.CharField(max_length=75)
    chemical_nature = models.CharField(max_length=75)
    origin = models.CharField(max_length=10, choices=[
        ('Natural', 'Natural'),
        ('Synthetic', 'Synthetic')
    ])
    analysis_required = models.CharField(max_length=75)

    def __str__(self):
        return "{} : {} {} {}".format(
            "Rheometer",
            str(self.date.day),
            calendar.month_name[self.date.month],
            str(self.date.year)
        )

    class Meta:
        verbose_name = 'Rheometer'
        verbose_name_plural = 'Rheometer'


class AAS(UserDetail, UserRemark):
    sample_code = models.CharField(max_length=75)
    elements = models.CharField(max_length=75)

    def __str__(self):
        return "{} : {} {} {}".format(
            "AAS",
            str(self.date.day),
            calendar.month_name[self.date.month],
            str(self.date.year)
        )

    class Meta:
        verbose_name = 'AAS'
        verbose_name_plural = 'AAS'


class TGA(UserDetail, UserRemark):
    sample_code = models.CharField(max_length=75)
    chemical_composition = models.CharField(max_length=75)
    sample_amount = models.CharField(max_length=75)
    heating_program = models.CharField(max_length=15, choices=[
        ('Dynamic', 'Dynamic'),
        ('Isothermal',
         'Isothermal'),
    ])
    temperature = models.CharField(max_length=75)
    atmosphere = models.CharField(max_length=5, choices=[
        ('N2', 'N2'),
        ('Ar', 'Ar'),
        ('Air', 'Air'),
    ])
    heating_rate = models.CharField(max_length=75)
    sample_solubility = models.CharField(max_length=75)

    def __str__(self):
        return "{} : {} {} {}".format(
            "TGA",
            str(self.date.day),
            calendar.month_name[self.date.month],
            str(self.date.year)
        )

    class Meta:
        verbose_name = 'TGA'
        verbose_name_plural = 'TGA'


class BET(UserDetail, UserRemark):
    sample_code = models.CharField(max_length=75)
    pretreatment_conditions = models.CharField(max_length=75)
    precautions = models.CharField(max_length=75)
    adsorption = models.CharField(max_length=75)
    surface_area = models.CharField(max_length=75)

    def __str__(self):
        return "{} : {} {} {}".format(
            "BET",
            str(self.date.day),
            calendar.month_name[self.date.month],
            str(self.date.year)
        )

    class Meta:
        verbose_name = 'BET'
        verbose_name_plural = 'BET'


class CDSpectrophotometer(UserDetail, UserRemark):
    sample_code = models.CharField(max_length=75)
    wavelength_scan_start = models.CharField(max_length=75)
    wavelength_scan_end = models.CharField(max_length=75)
    wavelength_fixed = models.CharField(max_length=75)
    temp_range_scan_start = models.CharField(max_length=75)
    temp_range_scan_end = models.CharField(max_length=75)
    temp_range_fixed = models.CharField(max_length=75)
    concentration = models.CharField(max_length=75)
    cell_path_length = models.CharField(max_length=75)

    def __str__(self):
        return "{} : {} {} {}".format(
            "CDSpectrophotometer",
            str(self.date.day),
            calendar.month_name[self.date.month],
            str(self.date.year)
        )

    class Meta:
        verbose_name = 'CDSpectrophotometer'
        verbose_name_plural = 'CDSpectrophotometer'


class LSCM(UserDetail, UserRemark):
    sample_description = models.CharField(max_length=75)
    dye = models.CharField(max_length=75)
    excitation_wavelength = models.CharField(max_length=75)
    emission_range = models.CharField(max_length=75)
    analysis_details = models.CharField(max_length=75)

    def __str__(self):
        return "{} : {} {} {}".format(
            "LSCM",
            str(self.date.day),
            calendar.month_name[self.date.month],
            str(self.date.year)
        )

    class Meta:
        verbose_name = 'LSCM'
        verbose_name_plural = 'LSCM'


class DSC(UserDetail, UserRemark):
    sample_code = models.CharField(max_length=75)
    chemical_composition = models.CharField(max_length=75)
    sample_amount = models.CharField(max_length=75)
    heating_program = models.CharField(max_length=15, choices=[
        ('Dynamic', 'Dynamic'),
        ('Isothermal',
         'Isothermal')
    ])
    temp_range = models.CharField(max_length=75)
    atmosphere = models.CharField(max_length=5, choices=[
        ('N2', 'N2'),
        ('Ar', 'Ar'),
        ('Air', 'Air'),
    ])
    heating_rate = models.CharField(max_length=75)

    def __str__(self):
        return "{} : {} {} {}".format(
            "DSC",
            str(self.date.day),
            calendar.month_name[self.date.month],
            str(self.date.year)
        )

    class Meta:
        verbose_name = 'DSC'
        verbose_name_plural = 'DSC'


class GC(UserDetail, UserRemark):
    sample_code = models.CharField(max_length=75)
    appearance = models.CharField(max_length=75)
    no_of_gc_peaks = models.IntegerField()
    solvent_solubility = models.CharField(max_length=75)
    column_details = models.CharField(max_length=75)
    exp_mol_wt = models.CharField(max_length=75)
    mp_bp = models.CharField(max_length=75)
    sample_source = models.CharField(max_length=15, choices=[
        ('Natural', 'Natural'),
        ('Synthesis', 'Synthesis'),
        ('Waste', 'Waste')
    ])

    def __str__(self):
        return "{} : {} {} {}".format(
            "GC",
            str(self.date.day),
            calendar.month_name[self.date.month],
            str(self.date.year)
        )

    class Meta:
        verbose_name = 'GC'
        verbose_name_plural = 'GC'


class EDXRF(UserDetail, UserRemark):
    sample_code = models.CharField(max_length=75)
    sample_nature = models.CharField(max_length=15, choices=[
        ('Powder', 'Powder'),
        ('Metal', 'Metal'),
        ('Film', 'Film'),
        ('Biological',
         'Biological'),
        ('Concrete', 'Concrete'),
    ])
    elements_present = models.CharField(max_length=75)

    def __str__(self):
        return "{} : {} {} {}".format(
            "EDXRF",
            str(self.date.day),
            calendar.month_name[self.date.month],
            str(self.date.year)
        )

    class Meta:
        verbose_name = 'EDXRF'
        verbose_name_plural = 'EDXRF'


class HLPCBase(models.Model):
    """Abstract base model for HLPC type instruments

    HLPC-type instruments (HLPC and HLPC-FD) uses the
    same form. This abstract model provides the common
    fields.
    """
    sample_code = models.CharField(max_length=75)
    sample_information = models.CharField(max_length=75)
    mobile_phase = models.CharField(max_length=75)
    column_for_lc = models.CharField(max_length=75)
    detection_wavelength = models.CharField(max_length=75)

    class Meta:
        abstract = True


class HPLC(UserDetail, UserRemark, HLPCBase):

    def __str__(self):
        return "{} : {} {} {}".format(
            "HPLC",
            str(self.date.day),
            calendar.month_name[self.date.month],
            str(self.date.year)
        )

    class Meta:
        verbose_name = 'HPLC'
        verbose_name_plural = 'HPLC'


class HPLC_FD(UserDetail, UserRemark, HLPCBase):
    def __str__(self):
        return "{} : {} {} {}".format(
            "HPLC-FD",
            str(self.date.day),
            calendar.month_name[self.date.month],
            str(self.date.year)
        )

    class Meta:
        verbose_name = 'HPLC-FD'
        verbose_name_plural = 'HPLC-FD'


class NMR(UserDetail, UserRemark):
    sample_code = models.CharField(max_length=75)
    sample_nature = models.CharField(max_length=10, choices=[
        ('Solid', 'Solid'),
        ('Liquid', 'Liquid'),
    ])
    quantity = models.CharField(max_length=75)
    solvent = models.CharField(max_length=75)
    analysis = models.CharField(max_length=75)
    experiment = models.CharField(max_length=75)
    spectral_range = models.CharField(max_length=75)

    def __str__(self):
        return "{} : {} {} {}".format(
            "NMR",
            str(self.date.day),
            calendar.month_name[self.date.month],
            str(self.date.year)
        )

    class Meta:
        verbose_name = 'NMR'
        verbose_name_plural = 'NMR'


class PXRD(UserDetail, UserRemark):
    sample_code = models.CharField(max_length=75)
    chemical_composition = models.CharField(max_length=75)
    sample_description = models.CharField(max_length=10, choices=[
        ('Film', 'Film'),
        ('Powder', 'Powder'),
        ('Pellet', 'Pellet'),
    ])
    range = models.CharField(max_length=75)
    scanning_rate = models.CharField(max_length=75)

    def __str__(self):
        return "{} : {} {} {}".format(
            "PXRD",
            str(self.date.day),
            calendar.month_name[self.date.month],
            str(self.date.year)
        )

    class Meta:
        verbose_name = 'PXRD'
        verbose_name_plural = 'PXRD'


class SAXS_WAXS(UserDetail, UserRemark):
    sample_code = models.CharField(max_length=75)
    nature_of_samples = models.CharField(max_length=10, choices=[
        ('Film', 'Film'),
        ('Liquid', 'Liquid'),
        ('Powder', 'Powder'),
        ('Other', 'Other'),
    ])

    def __str__(self):
        return "{} : {} {} {}".format(
            "SAXS/WAXS",
            str(self.date.day),
            calendar.month_name[self.date.month],
            str(self.date.year)
        )

    class Meta:
        verbose_name = 'SAXS/WAXS'
        verbose_name_plural = 'SAXS/WAXS'


class SCXRD(UserDetail, UserRemark):
    sample_code = models.CharField(max_length=75)
    chemical_composition = models.CharField(max_length=75)
    scanning_rate = models.CharField(max_length=75)
    source = models.CharField(max_length=5, choices=[
        ('Cu', 'Cu'),
        ('Mo', 'Mo'),
    ])

    def __str__(self):
        return "{} : {} {} {}".format(
            "SCXRD",
            str(self.date.day),
            calendar.month_name[self.date.month],
            str(self.date.year)
        )

    class Meta:
        verbose_name = 'SCXRD'
        verbose_name_plural = 'SCXRD'


class XPS(UserDetail, UserRemark):
    sample_name = models.CharField(max_length=75)
    sample_nature = models.CharField(max_length=75)
    chemical_composition = models.CharField(max_length=75)
    sample_property = models.CharField(max_length=20, choices=[
        ('Conducting', 'Conducting'),
        ('Semi Conducting',
         'Semi Conducting'),
        ('Insulating',
         'Insulating'),
    ])
    analysed_elements = models.CharField(max_length=75)
    scan_details = models.CharField(max_length=75)

    def __str__(self):
        return "{} : {} {} {}".format(
            "XPS",
            str(self.date.day),
            calendar.month_name[self.date.month],
            str(self.date.year)
        )

    class Meta:
        verbose_name = 'XPS'
        verbose_name_plural = 'XPS'


class UVSpectrophotometer(UserDetail, UserRemark):
    sample_code = models.CharField(max_length=75)
    sample_composition = models.CharField(max_length=75)
    molecular_weight = models.CharField(max_length=75)
    analysis_mode = models.CharField(max_length=10, choices=[
        ('Solid', 'Solid'),
        ('Liquid', 'Liquid'),
        ('Thin Film', 'Thin Film'),
    ])
    wavelength = models.CharField(max_length=75)
    ordinate_mode = models.CharField(max_length=75)

    def __str__(self):
        return "{} : {} {} {}".format(
            "UVSpectrophotometer",
            str(self.date.day),
            calendar.month_name[self.date.month],
            str(self.date.year)
        )

    class Meta:
        verbose_name = 'UVSpectrophotometer'
        verbose_name_plural = 'UVSpectrophotometer'


class UTM(UserDetail, UserRemark):
    TEST_TYPE_TENSILE = 'tensile'
    TEST_TYPE_COMPRESSION = 'compression'
    TEST_TYPE_3POINT_BENDING = '3-point-bending'
    TEST_TYPE_ILSS = 'ilss'
    TEST_TYPE_DOUBLE_CANT_BEAM = 'double-cant-beam'

    TEST_TYPE_CHOICES = (
        (TEST_TYPE_TENSILE, 'Tensile'),
        (TEST_TYPE_COMPRESSION, 'Compression'),
        (TEST_TYPE_3POINT_BENDING, '3 Point Bending'),
        (TEST_TYPE_ILSS, 'ILSS'),
        (TEST_TYPE_DOUBLE_CANT_BEAM, 'Double Cantilever Beam'),
    )

    material = models.CharField(max_length=75)
    test_type = models.CharField(max_length=75, choices=TEST_TYPE_CHOICES)
    test_speed = models.DecimalField(max_digits=9, decimal_places=4, help_text=(
        "<small>"
        "Precision upto 4 decimal places"
        "</small>"
    ))
    temperature = models.IntegerField(help_text=(
        "<small>"
        "The temperature ranges are as follows:</br>"
        "Room Temperature = 25°C</br>"
        "Temperature Chamber = -70°C - 250°C</br>"
        "Furnace = 250°C - 1200°C</br>"
        "Any additional remarks can be specified in the box below.</br>"
        "</small>"
    ))

    class Meta:
        verbose_name = 'UTM'
        verbose_name_plural = 'UTM'


class VSM(UserDetail, UserRemark):
    sample_code = models.CharField(max_length=75)
    sample_nature = models.CharField(max_length=10, choices=[
        ('Powder', 'Powder'),
        ('Pellet', 'Pellet'),
        ('Liquid', 'Liquid'),
    ])
    field = models.CharField(max_length=75)
    step_size = models.CharField(max_length=75)

    def __str__(self):
        return "{} : {} {} {}".format(
            "VSM",
            str(self.date.day),
            calendar.month_name[self.date.month],
            str(self.date.year)
        )

    class Meta:
        verbose_name = 'VSM'
        verbose_name_plural = 'VSM'
