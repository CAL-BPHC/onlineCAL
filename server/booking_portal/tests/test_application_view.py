import datetime

from django.contrib.contenttypes.models import ContentType
from django.test import Client, TestCase

from ..factories import FacultyFactory
from ..models import Student, StudentRequest
from .test_portal_filters import RequestBuilderMixin


class ApplicationViewTestCase(RequestBuilderMixin, TestCase):
    """The submitted application as a reviewer reads it."""

    def make_form(self, number_of_samples=1):
        # the view resolves the applicant and supervisor off the form object
        form = super().make_form(number_of_samples)
        form.user_type = ContentType.objects.get_for_model(Student)
        form.user_id = self.student.id
        form.sup_name = self.faculty
        form.sup_dept = str(self.department)
        form.save()
        return form

    def setUp(self):
        self.build_portal_fixtures()
        self.request = self.make_request(
            StudentRequest.WAITING_FOR_FACULTY, datetime.date(2026, 5, 4)
        )
        # The form only keeps a mode field for an instrument that config maps to
        # a priced one, which a factory built instrument is not. The mode row
        # itself is incidental to what these tests check.
        StudentRequest.objects.filter(pk=self.request.pk).update(
            mode_description="", mode_cost=0
        )
        self.request.refresh_from_db()
        self.client = Client()
        self.client.force_login(self.faculty)

    def url(self):
        return f"/application/view/{self.request.id}"

    def test_details_are_read_as_values_not_form_widgets(self):
        response = self.client.get(self.url())
        body = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertIn("Application details", body)
        self.assertIn("Number of samples", body)
        # the only input left is the remark box this faculty may still fill
        self.assertEqual(body.count("<textarea"), 1)
        self.assertNotIn("disabled", body.split("Application details")[1])

    def test_the_supervising_faculty_can_decide_from_the_application(self):
        body = self.client.get(self.url()).content.decode()

        self.assertIn("Accept request", body)
        self.assertIn("Reject request", body)
        self.assertIn(f"/requests_faculty/accept/{self.request.id}", body)

    def test_another_faculty_cannot_decide(self):
        stranger = FacultyFactory()
        client = Client()
        client.force_login(stranger)

        body = client.get(self.url()).content.decode()

        self.assertNotIn("Accept request", body)
        self.assertNotIn("Reject request", body)

    def test_a_request_already_acted_on_offers_no_decision(self):
        self.request.status = StudentRequest.WAITING_FOR_DEPARTMENT
        self.request.save()

        body = self.client.get(self.url()).content.decode()

        self.assertNotIn("Accept request", body)

    def test_accepting_from_the_application_moves_the_request(self):
        response = self.client.post(
            f"/requests_faculty/accept/{self.request.id}",
            {"departmentRoute": "True"},
            HTTP_REFERER=self.url(),
        )

        self.request.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.request.status, StudentRequest.WAITING_FOR_DEPARTMENT)

    def test_the_faculty_list_links_to_the_application_instead_of_deciding(self):
        body = self.client.get("/faculty/").content.decode()

        self.assertIn("Review &amp; decide", body)
        self.assertNotIn(f'href="/requests_faculty/accept/{self.request.id}"', body)
        self.assertNotIn("Accept</button>", body)
