"""Requests are billed to the department, whose approval is taken as given."""

import datetime
import importlib

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.test import Client, TestCase
from django.utils import timezone

from ..factories import FacultyFactory, InstrumentFactory, LabAssistantFactory
from ..models import Department, Faculty, FacultyRequest, Slot, StudentRequest
from ..models.email import EmailModel
from .test_portal_filters import RequestBuilderMixin

USAGE_URL = "/department/usage-summary"

skip_department_approval = importlib.import_module(
    "booking_portal.migrations.0076_skip_department_approval"
)


class BillingFixtureMixin(RequestBuilderMixin):
    def make_faculty_request(self, status, faculty=None, **kwargs):
        faculty = faculty or self.faculty
        form = self.make_form()
        form.user_type = ContentType.objects.get_for_model(Faculty)
        form.user_id = faculty.id
        form.save()
        return FacultyRequest.objects.create(
            faculty=faculty,
            instrument=kwargs.pop("instrument", self.instrument),
            slot=self.make_slot(kwargs.pop("date", datetime.date(2025, 6, 1))),
            status=status,
            mode_description="flat",
            mode_cost=kwargs.pop("cost", 100),
            mode_rule_type="FLAT",
            content_object=form,
            **kwargs,
        )

    def other_department_faculty(self):
        department = Department.objects.create(email="phy@example.com", name="physics")
        faculty = FacultyFactory()
        faculty.department = department
        faculty.save()
        return faculty


class FacultyAcceptTestCase(BillingFixtureMixin, TestCase):
    def setUp(self):
        self.build_portal_fixtures()
        self.client = Client()
        self.client.force_login(self.faculty)

    def test_accepting_sends_it_to_the_lab_assistant_without_an_email(self):
        request_obj = self.make_request(StudentRequest.WAITING_FOR_FACULTY)
        emails_before = EmailModel.objects.count()

        self.client.post(f"/requests_faculty/accept/{request_obj.id}")

        request_obj.refresh_from_db()
        self.assertEqual(request_obj.status, StudentRequest.WAITING_FOR_LAB_ASST)
        self.assertTrue(request_obj.needs_department_approval)
        self.assertEqual(EmailModel.objects.count(), emails_before)
        self.assertFalse(
            EmailModel.objects.filter(
                email_type=EmailModel.DEPARTMENT_APPROVAL
            ).exists()
        )

    def test_a_route_flag_left_in_an_old_page_changes_nothing(self):
        request_obj = self.make_request(StudentRequest.WAITING_FOR_FACULTY)

        self.client.post(
            f"/requests_faculty/accept/{request_obj.id}", {"departmentRoute": "True"}
        )

        request_obj.refresh_from_db()
        self.assertEqual(request_obj.status, StudentRequest.WAITING_FOR_LAB_ASST)


class FacultyBookingTestCase(TestCase):
    """A faculty's own booking goes straight to the lab assistant."""

    def setUp(self):
        from ..config import form_template_dict

        self.instrument_id = 3  # FTIR, as in FillInFormTestCase
        self.assertIn(self.instrument_id, form_template_dict)
        self.faculty = FacultyFactory()
        self.department = Department.objects.create(
            email="book@example.com", name="chemistry"
        )
        self.faculty.department = self.department
        self.faculty.save()
        self.instrument = InstrumentFactory(name="FTIR", pk=self.instrument_id)
        self.slot = Slot.objects.create(
            instrument=self.instrument,
            date=timezone.localdate() + datetime.timedelta(days=3),
            start_time=datetime.time(9),
            end_time=datetime.time(11),
            status=Slot.STATUS_1,
        )
        self.client = Client()
        self.client.force_login(self.faculty)

    def url(self):
        return f"/book-machine/{self.instrument_id}?slots={self.slot.id}"

    def filled_in(self, **extra):
        data = {
            "user_name": self.faculty.id,
            "phone_number": "9876543210",
            "date_day": self.slot.date.day,
            "date_month": self.slot.date.month,
            "date_year": self.slot.date.year,
            "time": "09:00",
            "duration": "2 hr",
            "number_of_samples": 2,
            "sample_from_outside": "No",
            "origin_of_sample": "lab",
            "req_discussed": "Yes",
            "sample_code": "SC-1",
            "composition": "NaCl",
            "state": "Solid",
            "solvent": "water",
        }
        data.update(extra)
        return data

    def test_the_form_no_longer_asks_for_department_approval(self):
        body = self.client.get(self.url()).content.decode()

        self.assertIn('name="phone_number"', body)
        self.assertNotIn("needs_department_approval", body)
        self.assertNotIn("department&#x27;s approval", body)

    def test_booking_goes_to_the_lab_assistant_billed_to_the_department(self):
        response = self.client.post(
            self.url(), self.filled_in(action="submit", calculation_done="True")
        )

        self.assertEqual(response.status_code, 302)
        request_obj = FacultyRequest.objects.get()
        self.assertEqual(request_obj.status, FacultyRequest.WAITING_FOR_LAB_ASST)
        self.assertTrue(request_obj.needs_department_approval)
        self.assertFalse(
            EmailModel.objects.filter(
                email_type=EmailModel.DEPARTMENT_APPROVAL
            ).exists()
        )

    def test_a_faculty_without_a_department_cannot_book(self):
        self.faculty.department = None
        self.faculty.save()

        page = self.client.get(self.url())
        submit = self.client.post(
            self.url(), self.filled_in(action="submit", calculation_done="True")
        )

        self.assertRedirects(page, "/instrument-list/", fetch_redirect_response=False)
        self.assertRedirects(submit, "/instrument-list/", fetch_redirect_response=False)
        self.assertFalse(FacultyRequest.objects.exists())


class LabAssistantChargesTheDepartmentTestCase(BillingFixtureMixin, TestCase):
    """The one place money moves, which the change must leave as it was."""

    def setUp(self):
        self.build_portal_fixtures()
        self.department.balance = 1000
        self.department.save()
        self.faculty.balance = 500
        self.faculty.save()
        self.client = Client()
        self.client.force_login(LabAssistantFactory())

    def assert_balances(self, department, faculty):
        self.department.refresh_from_db()
        self.faculty.refresh_from_db()
        self.assertEqual(self.department.balance, department)
        self.assertEqual(self.faculty.balance, faculty)

    def test_a_student_request_is_charged_to_the_department(self):
        request_obj = self.make_request(
            StudentRequest.WAITING_FOR_LAB_ASST,
            cost=150,
            needs_department_approval=True,
        )

        self.client.post(f"/requests_assistant/accept/{request_obj.id}")

        request_obj.refresh_from_db()
        self.assertEqual(request_obj.status, StudentRequest.APPROVED)
        self.assert_balances(department=850, faculty=500)

    def test_a_faculty_booking_is_charged_to_the_department(self):
        request_obj = self.make_faculty_request(
            FacultyRequest.WAITING_FOR_LAB_ASST,
            cost=150,
            needs_department_approval=True,
        )

        self.client.post(f"/requests_assistant/accept/{request_obj.id}?is_faculty=true")

        request_obj.refresh_from_db()
        self.assertEqual(request_obj.status, FacultyRequest.APPROVED)
        self.assert_balances(department=850, faculty=500)

    def test_rejecting_charges_nobody(self):
        request_obj = self.make_request(
            StudentRequest.WAITING_FOR_LAB_ASST,
            cost=150,
            needs_department_approval=True,
        )

        self.client.post(f"/requests_assistant/reject/{request_obj.id}")

        self.assert_balances(department=1000, faculty=500)


class MigrationTestCase(BillingFixtureMixin, TestCase):
    def setUp(self):
        self.build_portal_fixtures()

    def test_upcoming_requests_move_on_to_the_lab_assistant_silently(self):
        today = timezone.localdate()
        upcoming = self.make_request(
            StudentRequest.WAITING_FOR_DEPARTMENT,
            today + datetime.timedelta(days=2),
            needs_department_approval=True,
        )
        on_the_day = self.make_request(
            StudentRequest.WAITING_FOR_DEPARTMENT,
            today,
            needs_department_approval=True,
        )
        faculty_request = self.make_faculty_request(
            FacultyRequest.WAITING_FOR_DEPARTMENT,
            date=today + datetime.timedelta(days=2),
            needs_department_approval=True,
        )
        untouched = self.make_request(
            StudentRequest.WAITING_FOR_FACULTY, today + datetime.timedelta(days=2)
        )
        emails_before = EmailModel.objects.count()

        skip_department_approval.move_to_lab_assistant(apps, None)

        for request_obj, status in (
            (upcoming, StudentRequest.WAITING_FOR_LAB_ASST),
            (on_the_day, StudentRequest.WAITING_FOR_LAB_ASST),
            (faculty_request, FacultyRequest.WAITING_FOR_LAB_ASST),
            (untouched, StudentRequest.WAITING_FOR_FACULTY),
        ):
            request_obj.refresh_from_db()
            self.assertEqual(request_obj.status, status)
        self.assertTrue(upcoming.needs_department_approval)
        self.assertEqual(EmailModel.objects.count(), emails_before)

    def test_past_requests_are_left_waiting_on_the_department(self):
        past = self.make_request(
            StudentRequest.WAITING_FOR_DEPARTMENT,
            timezone.localdate() - datetime.timedelta(days=1),
            needs_department_approval=True,
        )
        past_faculty_request = self.make_faculty_request(
            FacultyRequest.WAITING_FOR_DEPARTMENT,
            date=datetime.date(2024, 9, 1),
            needs_department_approval=True,
        )

        skip_department_approval.move_to_lab_assistant(apps, None)

        for request_obj in (past, past_faculty_request):
            request_obj.refresh_from_db()
            self.assertEqual(request_obj.status, StudentRequest.WAITING_FOR_DEPARTMENT)

    def test_queued_department_emails_are_dropped_and_nothing_else(self):
        def queue(email_type, sent):
            return EmailModel.objects.create(
                receiver="x@example.com",
                text="t",
                text_html="t",
                subject="s",
                sent=sent,
                email_type=email_type,
            )

        stale = queue(EmailModel.DEPARTMENT_APPROVAL, sent=False)
        history = queue(EmailModel.DEPARTMENT_APPROVAL, sent=True)
        other = queue(EmailModel.BOOKING_APPROVED, sent=False)

        skip_department_approval.drop_queued_department_emails(apps, None)

        self.assertFalse(EmailModel.objects.filter(pk=stale.pk).exists())
        self.assertTrue(EmailModel.objects.filter(pk=history.pk).exists())
        self.assertTrue(EmailModel.objects.filter(pk=other.pk).exists())


class DepartmentPortalTestCase(BillingFixtureMixin, TestCase):
    def setUp(self):
        self.build_portal_fixtures()
        self.client = Client()
        self.client.force_login(self.department)

    def test_the_list_is_read_only(self):
        self.make_request(
            StudentRequest.WAITING_FOR_LAB_ASST, needs_department_approval=True
        )
        self.make_faculty_request(
            FacultyRequest.WAITING_FOR_LAB_ASST, needs_department_approval=True
        )

        body = self.client.get("/department/").content.decode()

        self.assertNotIn(">Actions</th>", body)
        self.assertNotIn("Accept</button>", body)
        self.assertNotIn("Reject</button>", body)
        self.assertNotIn("confirmationModal", body)
        self.assertNotIn("/requests_department/", body)

    def test_the_list_says_who_the_student_was(self):
        self.make_request(
            StudentRequest.WAITING_FOR_LAB_ASST, needs_department_approval=True
        )
        self.make_faculty_request(
            FacultyRequest.WAITING_FOR_LAB_ASST, needs_department_approval=True
        )

        body = self.client.get("/department/").content.decode()

        self.assertIn(">Student Name</th>", body)
        self.assertIn(f"<td>{self.student}</td>", body)
        # a faculty's own booking has no student
        self.assertIn("<td>&mdash;</td>", body)

    def test_the_usage_panel_is_the_departments(self):
        body = self.client.get("/department/").content.decode()

        self.assertIn('id="usagePanel"', body)
        self.assertIn(f'data-usage-url="{USAGE_URL}"', body)
        self.assertIn("Department Usage", body)
        self.assertIn('data-group="by_faculty"', body)
        self.assertNotIn('data-group="by_student"', body)
        self.assertNotIn("Approval queue", body)
        self.assertNotIn("balance", body.lower())

    def test_an_invalid_filter_does_not_show_other_departments(self):
        mine = self.make_request(
            StudentRequest.WAITING_FOR_LAB_ASST, needs_department_approval=True
        )
        theirs = self.make_request(
            StudentRequest.WAITING_FOR_LAB_ASST,
            faculty=self.other_department_faculty(),
            needs_department_approval=True,
        )

        for query in ("", "?status=bogus", "?from_date=not-a-date"):
            with self.subTest(query=query):
                page = self.client.get(f"/department/{query}")
                ids = [request_obj.pk for request_obj in page.context["page_obj"]]

                self.assertIn(mine.pk, ids)
                self.assertNotIn(theirs.pk, ids)


class DepartmentUsageTestCase(BillingFixtureMixin, TestCase):
    def setUp(self):
        self.build_portal_fixtures()
        self.client = Client()
        self.client.force_login(self.department)

    def usage(self, **params):
        response = self.client.get(USAGE_URL, {"preset": "all_time", **params})
        self.assertEqual(response.status_code, 200)
        return response.json()

    def test_usage_is_grouped_by_faculty(self):
        colleague = FacultyFactory()
        colleague.department = self.department
        colleague.save()
        self.make_request(
            StudentRequest.APPROVED, hours=2, cost=100, needs_department_approval=True
        )
        self.make_faculty_request(
            FacultyRequest.APPROVED, cost=50, needs_department_approval=True
        )
        self.make_request(
            StudentRequest.APPROVED,
            hours=3,
            cost=300,
            faculty=colleague,
            needs_department_approval=True,
        )

        payload = self.usage()

        self.assertEqual(
            payload["totals"],
            {"key": "totals", "hours": 7.0, "cost": 450.0, "bookings": 3},
        )
        by_faculty = {row["key"]: row for row in payload["by_faculty"]}
        self.assertEqual(by_faculty[str(self.faculty)]["hours"], 4.0)
        self.assertEqual(by_faculty[str(self.faculty)]["cost"], 150.0)
        self.assertEqual(by_faculty[str(self.faculty)]["bookings"], 2)
        self.assertEqual(by_faculty[str(colleague)]["cost"], 300.0)
        self.assertEqual(
            [child["key"] for child in by_faculty[str(colleague)]["children"]],
            ["FTIR"],
        )
        # the biggest user comes first
        self.assertEqual(payload["by_faculty"][0]["key"], str(self.faculty))
        self.assertEqual(payload["by_instrument"][0]["key"], "FTIR")
        self.assertEqual(payload["by_instrument"][0]["bookings"], 3)

    def test_only_what_is_billed_to_this_department_counts(self):
        self.make_request(
            StudentRequest.APPROVED,
            faculty=self.other_department_faculty(),
            needs_department_approval=True,
        )
        # paid for by the faculty before every request went through the department
        self.make_request(StudentRequest.APPROVED, needs_department_approval=False)

        payload = self.usage()

        self.assertEqual(payload["totals"]["bookings"], 0)
        self.assertEqual(payload["by_faculty"], [])

    def test_what_never_happened_is_never_counted(self):
        for status in (StudentRequest.REJECTED, StudentRequest.CANCELLED):
            self.make_request(status, needs_department_approval=True)

        self.assertEqual(self.usage()["totals"]["bookings"], 0)
        for status in (StudentRequest.REJECTED, StudentRequest.CANCELLED):
            with self.subTest(status=status):
                payload = self.usage(status=status)
                self.assertEqual(payload["totals"]["bookings"], 0)
                self.assertFalse(payload["basis"]["counts_towards_usage"])

    def test_pending_is_what_the_lab_assistant_has_still_to_approve(self):
        self.make_request(
            StudentRequest.WAITING_FOR_LAB_ASST,
            hours=2,
            cost=120,
            needs_department_approval=True,
        )
        self.make_faculty_request(
            FacultyRequest.WAITING_FOR_LAB_ASST, cost=80, needs_department_approval=True
        )
        self.make_request(StudentRequest.APPROVED, needs_department_approval=True)

        payload = self.usage()

        self.assertEqual(payload["pending"]["bookings"], 2)
        self.assertEqual(payload["pending"]["cost"], 200.0)
        # pending is not usage yet
        self.assertEqual(payload["totals"]["bookings"], 1)

    def test_the_range_and_instrument_narrow_it(self):
        other = InstrumentFactory(name="XRD")
        self.make_request(
            StudentRequest.APPROVED,
            datetime.date(2025, 6, 1),
            needs_department_approval=True,
        )
        self.make_request(
            StudentRequest.APPROVED,
            datetime.date(2024, 6, 1),
            needs_department_approval=True,
        )
        self.make_request(
            StudentRequest.APPROVED,
            datetime.date(2025, 6, 2),
            instrument=other,
            needs_department_approval=True,
        )

        in_fy = self.client.get(
            USAGE_URL, {"preset": "custom", "from": "2025-04-01", "to": "2026-03-31"}
        ).json()
        ftir_only = self.usage(instrument=self.instrument.pk)

        self.assertEqual(in_fy["totals"]["bookings"], 2)
        self.assertEqual(ftir_only["totals"]["bookings"], 2)
        self.assertEqual(ftir_only["range"]["instrument"], "FTIR")

    def test_bad_parameters_are_rejected(self):
        for params in (
            {"preset": "nope"},
            {"preset": "custom"},
            {"instrument": 99999},
            {"status": "R9"},
        ):
            with self.subTest(params=params):
                self.assertEqual(self.client.get(USAGE_URL, params).status_code, 400)

    def test_only_a_department_can_read_it(self):
        for user in (self.faculty, self.student, LabAssistantFactory()):
            with self.subTest(user=user.role):
                client = Client()
                client.force_login(user)
                self.assertEqual(client.get(USAGE_URL).status_code, 302)
