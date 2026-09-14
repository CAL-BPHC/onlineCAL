import datetime

from django.test import TestCase

from ..models import Department, StudentRequest
from ..models.email import EmailModel
from .test_portal_filters import RequestBuilderMixin


class DepartmentSalutationTestCase(RequestBuilderMixin, TestCase):
    def test_department_names_are_turned_into_a_hod_greeting(self):
        cases = {
            "PHARMACY": "HOD of Pharmacy Department",
            "chemistry": "HOD of Chemistry Department",
            "CHEMICAL ENGINEERING": "HOD of Chemical Engineering Department",
        }
        for name, expected in cases.items():
            with self.subTest(name=name):
                self.assertEqual(Department(name=name).salutation, expected)

    def test_the_department_pending_email_greets_the_hod(self):
        self.build_portal_fixtures()
        self.department.name = "PHARMACY"
        self.department.save()

        self.make_request(
            StudentRequest.WAITING_FOR_DEPARTMENT, datetime.date(2026, 5, 4)
        )

        email = EmailModel.objects.get(email_type=EmailModel.DEPARTMENT_APPROVAL)
        self.assertEqual(email.receiver, self.department.email)
        self.assertIn("Dear HOD of Pharmacy Department,", email.text)
        self.assertIn("Dear HOD of Pharmacy Department,", email.text_html)
        self.assertNotIn("Dear PHARMACY", email.text)
