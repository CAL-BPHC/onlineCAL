from django.test import TestCase

from ..forms.instrument_requests import FESEMForm, FTIRForm


class SampleLimitTestCase(TestCase):
    """A form with max_samples caps number_of_samples; the rest stay open."""

    def test_fesem_rejects_more_than_three_samples(self):
        form = FESEMForm(data={"number_of_samples": 4})
        form.is_valid()

        self.assertIn("number_of_samples", form.errors)
        self.assertIn("less than or equal to 3", str(form.errors["number_of_samples"]))

    def test_fesem_accepts_three_samples(self):
        form = FESEMForm(data={"number_of_samples": 3})
        form.is_valid()

        self.assertNotIn("number_of_samples", form.errors)

    def test_the_cap_reaches_the_browser_control(self):
        field = FESEMForm().fields["number_of_samples"]

        self.assertEqual(field.widget.attrs["max"], 3)
        self.assertIn("3", field.help_text)

    def test_an_instrument_without_a_cap_is_unchanged(self):
        form = FTIRForm(data={"number_of_samples": 40})
        form.is_valid()

        self.assertNotIn("number_of_samples", form.errors)
        self.assertNotIn("max", form.fields["number_of_samples"].widget.attrs)
