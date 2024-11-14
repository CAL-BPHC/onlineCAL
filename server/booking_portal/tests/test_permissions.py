from django.test import TestCase

from ..factories import FacultyFactory, LabAssistantFactory, StudentFactory
from ..permissions import is_faculty, is_lab_assistant, is_student


class PermissionTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.student = StudentFactory()
        cls.faculty = FacultyFactory()
        cls.lab_asst = LabAssistantFactory()

    def test_is_student(self):
        self.assertTrue(is_student(PermissionTestCase.student))
        self.assertFalse(is_student(PermissionTestCase.faculty))
        self.assertFalse(is_student(PermissionTestCase.lab_asst))

    def test_is_faculty(self):
        self.assertTrue(is_faculty(PermissionTestCase.faculty))
        self.assertFalse(is_faculty(PermissionTestCase.student))
        self.assertFalse(is_faculty(PermissionTestCase.lab_asst))

    def test_is_lab_assistant(self):
        self.assertTrue(is_lab_assistant(PermissionTestCase.lab_asst))
        self.assertFalse(is_lab_assistant(PermissionTestCase.student))
        self.assertFalse(is_lab_assistant(PermissionTestCase.faculty))
