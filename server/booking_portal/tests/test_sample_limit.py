from django.test import TestCase

from ..forms.instrument_requests import (
    BETForm,
    ConfocalRamanSpectrometerForm,
    FESEMForm,
    FTIRForm,
    QuantachromeForm,
    XPSForm,
)

# Every form that caps its sample count, and the cap the lab asked for.
CAPPED_FORMS = {
    FESEMForm: 3,
    XPSForm: 4,
    ConfocalRamanSpectrometerForm: 4,
    BETForm: 3,
    QuantachromeForm: 2,
}


class SampleLimitTestCase(TestCase):
    """A form with max_samples caps number_of_samples; the rest stay open."""

    def test_the_cap_is_the_one_the_lab_asked_for(self):
        for form_class, cap in CAPPED_FORMS.items():
            with self.subTest(form=form_class.__name__):
                self.assertEqual(form_class.max_samples, cap)

    def test_one_sample_over_the_cap_is_rejected(self):
        for form_class, cap in CAPPED_FORMS.items():
            with self.subTest(form=form_class.__name__):
                form = form_class(data={"number_of_samples": cap + 1})
                form.is_valid()

                self.assertIn("number_of_samples", form.errors)
                self.assertIn(
                    f"less than or equal to {cap}",
                    str(form.errors["number_of_samples"]),
                )

    def test_the_cap_itself_is_accepted(self):
        for form_class, cap in CAPPED_FORMS.items():
            with self.subTest(form=form_class.__name__):
                form = form_class(data={"number_of_samples": cap})
                form.is_valid()

                self.assertNotIn("number_of_samples", form.errors)

    def test_the_cap_reaches_the_browser_control(self):
        for form_class, cap in CAPPED_FORMS.items():
            with self.subTest(form=form_class.__name__):
                field = form_class().fields["number_of_samples"]

                self.assertEqual(field.widget.attrs["max"], cap)
                self.assertIn(str(cap), field.help_text)

    def test_an_instrument_without_a_cap_is_unchanged(self):
        form = FTIRForm(data={"number_of_samples": 40})
        form.is_valid()

        self.assertNotIn("number_of_samples", form.errors)
        self.assertNotIn("max", form.fields["number_of_samples"].widget.attrs)


class RamanScanRangeTestCase(TestCase):
    """A blank scan range is reported, not crashed on."""

    def test_a_blank_scan_range_is_a_validation_error(self):
        form = ConfocalRamanSpectrometerForm(data={"number_of_samples": 1})

        self.assertFalse(form.is_valid())
        self.assertIn("scan_range_start", form.errors)
        self.assertIn("scan_range_end", form.errors)

    def test_an_inverted_scan_range_is_still_rejected(self):
        form = ConfocalRamanSpectrometerForm(
            data={"scan_range_start": 800, "scan_range_end": 200, "wavelength": 532}
        )
        form.is_valid()

        self.assertIn("scan_range_end", form.errors)
        self.assertIn("greater than", str(form.errors["scan_range_end"]))
