from django.test import TestCase

from ..models import Department


class DepartmentSalutationTestCase(TestCase):
    def test_department_names_are_turned_into_a_hod_greeting(self):
        cases = {
            "PHARMACY": "HOD of Pharmacy Department",
            "chemistry": "HOD of Chemistry Department",
            "CHEMICAL ENGINEERING": "HOD of Chemical Engineering Department",
        }
        for name, expected in cases.items():
            with self.subTest(name=name):
                self.assertEqual(Department(name=name).salutation, expected)
