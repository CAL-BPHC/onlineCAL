import datetime

from django.contrib.contenttypes.models import ContentType
from django.test import Client, TestCase

from ..factories import FacultyFactory, LabAssistantFactory
from ..models import Department, Student, StudentRequest
from .test_portal_filters import RequestBuilderMixin


class ApplicationFixtureMixin(RequestBuilderMixin):
    def make_form(self, number_of_samples=1):
        # the view resolves the applicant and supervisor off the form object
        form = super().make_form(number_of_samples)
        form.user_type = ContentType.objects.get_for_model(Student)
        form.user_id = self.student.id
        form.sup_name = self.faculty
        form.sup_dept = str(self.department)
        form.save()
        return form


class ApplicationViewTestCase(ApplicationFixtureMixin, TestCase):
    """The submitted application as a reviewer reads it."""

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

    def test_remarks_show_only_once_someone_has_written_one(self):
        body = self.client.get(self.url()).content.decode()

        self.assertNotIn(">Remarks</p>", body)

        form = self.request.content_object
        form.student_remarks = "Sample is air sensitive."
        form.save()
        body = self.client.get(self.url()).content.decode()

        self.assertIn(">Remarks</p>", body)
        self.assertIn("Sample is air sensitive.", body)

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
        # a {# #} comment cannot span lines; one that does renders as page text
        self.assertNotIn("{#", body)
        # nothing to press on a row this faculty cannot act on
        self.assertNotIn(
            '<button type="button" class="btn btn-success" disabled>', body
        )
        self.assertNotIn(f'href="/requests_faculty/accept/{self.request.id}"', body)
        self.assertNotIn("Accept</button>", body)


class ReturnAfterDecidingTestCase(ApplicationFixtureMixin, TestCase):
    """Deciding sends the faculty back to the list they were working through."""

    def setUp(self):
        self.build_portal_fixtures()
        self.request = self.make_request(StudentRequest.WAITING_FOR_FACULTY)
        StudentRequest.objects.filter(pk=self.request.pk).update(mode_description="")
        self.client = Client()
        self.client.force_login(self.faculty)

    def test_the_filtered_list_is_carried_into_the_decision(self):
        listing = "/faculty/?status=R1&page=1"

        page = self.client.get(
            f"/application/view/{self.request.id}",
            HTTP_REFERER=f"http://testserver{listing}",
        )

        # the attribute is escaped in the markup, as it should be
        self.assertContains(
            page,
            'name="next" value="http://testserver/faculty/?status=R1&amp;page=1"',
        )

    def test_deciding_returns_to_that_list(self):
        listing = "http://testserver/faculty/?status=R1"

        response = self.client.post(
            f"/requests_faculty/accept/{self.request.id}",
            {"departmentRoute": "True", "next": listing},
        )

        self.assertEqual(response["Location"], listing)

    def test_an_off_site_return_target_is_refused(self):
        response = self.client.post(
            f"/requests_faculty/accept/{self.request.id}",
            {"departmentRoute": "True", "next": "https://evil.example.com/"},
        )

        self.assertEqual(response["Location"], "/faculty/")

    def test_the_application_page_is_never_the_return_target(self):
        page = self.client.get(
            f"/application/view/{self.request.id}",
            HTTP_REFERER=f"http://testserver/application/view/{self.request.id}",
        )

        self.assertContains(page, 'name="next" value="/faculty/"')


class ReviewerDecisionTestCase(ApplicationFixtureMixin, TestCase):
    """Every reviewer decides from the application, each in their own state."""

    def setUp(self):
        self.build_portal_fixtures()
        self.client = Client()

    def open_as(self, user, request_obj):
        StudentRequest.objects.filter(pk=request_obj.pk).update(mode_description="")
        self.client.force_login(user)
        return self.client.get(f"/application/view/{request_obj.id}").content.decode()

    def test_the_department_decides_on_a_request_waiting_on_it(self):
        request_obj = self.make_request(
            StudentRequest.WAITING_FOR_DEPARTMENT, needs_department_approval=True
        )

        body = self.open_as(self.department, request_obj)

        self.assertIn("Accept request", body)
        self.assertIn(f"/requests_department/accept/{request_obj.id}", body)
        self.assertIn(f"/requests_department/reject/{request_obj.id}", body)

    def test_the_department_does_not_see_its_own_name_back(self):
        request_obj = self.make_request(
            StudentRequest.WAITING_FOR_DEPARTMENT, needs_department_approval=True
        )

        body = self.open_as(self.department, request_obj)

        # its own department is the one row it cannot learn anything from
        self.assertNotIn("Supervisor Department", body)
        self.assertIn("Supervisor Name", body)

    def test_another_department_decides_nothing(self):
        stranger = Department.objects.create(email="other@example.com", name="physics")
        request_obj = self.make_request(
            StudentRequest.WAITING_FOR_DEPARTMENT, needs_department_approval=True
        )

        body = self.open_as(stranger, request_obj)

        self.assertNotIn("Accept request", body)
        self.assertIn("Supervisor Department", body)

    def test_the_department_cannot_decide_before_its_turn(self):
        request_obj = self.make_request(StudentRequest.WAITING_FOR_FACULTY)

        self.assertNotIn("Accept request", self.open_as(self.department, request_obj))

    def test_accepting_as_the_department_moves_the_request_on(self):
        request_obj = self.make_request(
            StudentRequest.WAITING_FOR_DEPARTMENT, needs_department_approval=True
        )
        self.client.force_login(self.department)

        response = self.client.post(
            f"/requests_department/accept/{request_obj.id}",
            {"next": "http://testserver/department/?status=R6"},
        )

        request_obj.refresh_from_db()
        self.assertEqual(request_obj.status, StudentRequest.WAITING_FOR_LAB_ASST)
        self.assertEqual(
            response["Location"], "http://testserver/department/?status=R6"
        )

    def test_the_lab_assistant_decides_on_a_request_waiting_on_it(self):
        request_obj = self.make_request(StudentRequest.WAITING_FOR_LAB_ASST)

        body = self.open_as(LabAssistantFactory(), request_obj)

        self.assertIn("Accept request", body)
        self.assertIn(f"/requests_assistant/accept/{request_obj.id}", body)

    def test_the_lab_assistant_cannot_decide_before_its_turn(self):
        request_obj = self.make_request(StudentRequest.WAITING_FOR_DEPARTMENT)

        body = self.open_as(LabAssistantFactory(), request_obj)

        self.assertNotIn("Accept request", body)

    def test_accepting_as_the_lab_assistant_approves_the_request(self):
        request_obj = self.make_request(
            StudentRequest.WAITING_FOR_LAB_ASST, needs_department_approval=True
        )
        self.client.force_login(LabAssistantFactory())

        response = self.client.post(
            f"/requests_assistant/accept/{request_obj.id}",
            {"next": "http://testserver/lab-assistant/?status=R2"},
        )

        request_obj.refresh_from_db()
        self.assertEqual(request_obj.status, StudentRequest.APPROVED)
        self.assertEqual(
            response["Location"], "http://testserver/lab-assistant/?status=R2"
        )

    def test_a_return_target_for_another_portal_is_refused(self):
        request_obj = self.make_request(
            StudentRequest.WAITING_FOR_DEPARTMENT, needs_department_approval=True
        )
        self.client.force_login(self.department)

        response = self.client.post(
            f"/requests_department/accept/{request_obj.id}",
            {"next": "http://testserver/faculty/"},
        )

        self.assertEqual(response["Location"], "/department/")
