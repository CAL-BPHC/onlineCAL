import csv
import datetime
import importlib
import io

from django.apps import apps
from django.contrib import admin
from django.test import Client, TestCase
from django.utils import timezone

from ..admin.user import StudentAdmin
from ..factories import (
    CustomUserFaker,
    FacultyFactory,
    InstrumentFactory,
    LabAssistantFactory,
    StudentFactory,
)
from ..models import (
    CustomUser,
    Department,
    EmailModel,
    Slot,
    Student,
    StudentRequest,
)
from .test_portal_filters import RequestBuilderMixin

ACCESS_URL = "/admin-portal/instrument-access"


def portal_admin_lab_assistant():
    """A lab assistant made a portal admin, as make_portal_admin does."""
    user = LabAssistantFactory()
    user.role = CustomUser.Role.PORTAL_ADMIN
    user.save()
    return user


def open_slot(instrument):
    return Slot.objects.create(
        instrument=instrument,
        date=timezone.localdate() + datetime.timedelta(days=3),
        start_time=datetime.time(9),
        end_time=datetime.time(11),
        status=Slot.STATUS_1,
    )


class StudentBookingTestCase(TestCase):
    """A student books only the instruments assigned to them."""

    def setUp(self):
        self.student = StudentFactory()
        self.assigned = InstrumentFactory(name="FTIR", pk=3)  # the FTIR form
        self.other = InstrumentFactory(name="NMR")
        self.student.instruments.add(self.assigned)
        self.client = Client()
        self.client.force_login(self.student)

    def test_only_assigned_instruments_are_offered(self):
        response = self.client.get("/instrument-list/")

        self.assertContains(response, "You can book only the instruments assigned")
        self.assertContains(response, ">FTIR</option>")
        self.assertNotContains(response, ">NMR</option>")

    def test_a_student_with_nothing_assigned_is_told_so(self):
        self.student.instruments.clear()

        response = self.client.get("/instrument-list/")

        self.assertContains(response, "No instruments are assigned to you yet")
        self.assertNotContains(response, "<select")

    def test_slots_are_listed_only_for_an_assigned_instrument(self):
        refused = self.client.post("/view-slots/", {"instruments": self.other.pk})
        listed = self.client.post("/view-slots/", {"instruments": self.assigned.pk})

        self.assertRedirects(
            refused, "/instrument-list/", fetch_redirect_response=False
        )
        self.assertContains(listed, "Viewing slots for FTIR")

    def test_the_booking_form_goes_by_the_slot_not_the_url(self):
        # the FTIR form, but a slot of the instrument not assigned
        refused = self.client.get(f"/book-machine/3?slots={open_slot(self.other).pk}")
        opened = self.client.get(f"/book-machine/3?slots={open_slot(self.assigned).pk}")

        self.assertRedirects(
            refused, "/instrument-list/", fetch_redirect_response=False
        )
        self.assertEqual(opened.status_code, 200)

    def test_a_booking_of_an_unassigned_instrument_is_refused(self):
        slot = open_slot(self.other)

        with self.assertRaisesMessage(ValueError, "Instrument is not assigned to you."):
            # refused before the form is read
            StudentRequest.objects.create_request(None, slot.pk, self.student)

        slot.refresh_from_db()
        self.assertEqual(slot.status, Slot.STATUS_1)


class FacultyBookingTestCase(TestCase):
    def test_faculty_are_offered_every_instrument_without_the_banner(self):
        InstrumentFactory(name="FTIR")
        InstrumentFactory(name="NMR")
        client = Client()
        client.force_login(FacultyFactory())

        response = client.get("/instrument-list/")

        self.assertContains(response, ">FTIR</option>")
        self.assertContains(response, ">NMR</option>")
        self.assertNotContains(response, "assigned to you")


class InstrumentAccessPageTestCase(TestCase):
    """Portal admins assign a student an instrument after training, or revoke it."""

    def setUp(self):
        self.student = StudentFactory(name="Asha Rao")
        self.ftir = InstrumentFactory(name="FTIR")
        self.nmr = InstrumentFactory(name="NMR")
        self.client = Client()
        self.client.force_login(portal_admin_lab_assistant())

    def url(self):
        return f"{ACCESS_URL}/{self.student.pk}"

    def test_portal_admins_are_shown_it(self):
        for user in (portal_admin_lab_assistant(), CustomUserFaker()):
            with self.subTest(is_lab_assistant=hasattr(user, "labassistant")):
                self.client.force_login(user)

                for url in (ACCESS_URL, self.url()):
                    self.assertEqual(self.client.get(url).status_code, 200)
                self.assertContains(self.client.get("/"), "Instrument Access")

    def test_no_one_else_can_use_it(self):
        lab_assistant = LabAssistantFactory()
        department = Department.objects.create(email="d@example.com", name="chem")
        for user in (lab_assistant, self.student, self.student.supervisor, department):
            with self.subTest(role=user.role):
                self.client.force_login(user)

                for url in (ACCESS_URL, self.url()):
                    self.assertEqual(self.client.get(url).status_code, 302)
                assign = {"instrument": self.ftir.pk, "action": "assign"}
                self.client.post(self.url(), assign)
                self.client.post(ACCESS_URL, {**assign, "students": self.student.pk})

        self.assertFalse(self.student.instruments.exists())
        self.client.force_login(lab_assistant)
        self.assertNotContains(self.client.get("/lab-assistant/"), "Instrument Access")

    def test_students_are_found_by_name_or_email_or_instrument(self):
        other = StudentFactory(name="Ravi Kumar", email="ravi@example.com")
        other.instruments.add(self.nmr)

        by_name = self.client.get(ACCESS_URL, {"q": "asha"})
        by_email = self.client.get(ACCESS_URL, {"q": "ravi@"})
        by_instrument = self.client.get(ACCESS_URL, {"instrument": self.nmr.pk})

        self.assertContains(by_name, "Asha Rao")
        self.assertNotContains(by_name, "Ravi Kumar")
        self.assertContains(by_email, "Ravi Kumar")
        self.assertNotContains(by_email, "Asha Rao")
        self.assertContains(by_instrument, "Ravi Kumar")
        self.assertNotContains(by_instrument, "Asha Rao")

    def test_several_students_are_found_at_once(self):
        StudentFactory(name="Ravi Kumar")
        StudentFactory(name="Meena Iyer")

        response = self.client.get(ACCESS_URL, {"q": "asha, ravi,"})

        self.assertContains(response, "Asha Rao")
        self.assertContains(response, "Ravi Kumar")
        self.assertNotContains(response, "Meena Iyer")

    def test_ticked_students_are_assigned_or_revoked_together(self):
        ravi = StudentFactory(name="Ravi Kumar")
        meena = StudentFactory(name="Meena Iyer")  # not ticked
        meena.instruments.add(self.ftir)
        self.student.instruments.add(self.nmr)
        ticked = {"students": [self.student.pk, ravi.pk], "instrument": self.ftir.pk}

        assigned = self.client.post(
            f"{ACCESS_URL}?q=a", {**ticked, "action": "assign"}, follow=True
        )
        self.assertCountEqual(self.ftir.students.all(), [self.student, ravi, meena])
        revoked = self.client.post(ACCESS_URL, {**ticked, "action": "revoke"})

        # back to the same search, saying what changed
        self.assertEqual(assigned.redirect_chain, [(f"{ACCESS_URL}?q=a", 302)])
        self.assertContains(assigned, "2 students can now book FTIR.")
        self.assertRedirects(revoked, ACCESS_URL, fetch_redirect_response=False)
        self.assertCountEqual(self.ftir.students.all(), [meena])
        self.assertCountEqual(self.student.instruments.all(), [self.nmr])

    def test_nothing_ticked_changes_nothing(self):
        response = self.client.post(
            ACCESS_URL, {"instrument": self.ftir.pk, "action": "assign"}, follow=True
        )

        self.assertContains(response, "Tick at least one student")
        self.assertFalse(self.ftir.students.exists())

    def test_the_page_offers_to_revoke_what_is_assigned_and_assign_the_rest(self):
        self.student.instruments.add(self.ftir)

        body = self.client.get(self.url()).content.decode()

        self.assertIn("Can book (1)", body)
        self.assertIn(f'<option value="{self.nmr.pk}">NMR</option>', body)
        self.assertNotIn(f'<option value="{self.ftir.pk}">', body)

    def test_assigning_and_revoking_change_one_instrument_each(self):
        # assigned by another admin since this page was opened
        self.student.instruments.add(self.nmr)

        assigned = self.client.post(
            self.url(), {"instrument": self.ftir.pk, "action": "assign"}
        )
        self.assertCountEqual(self.student.instruments.all(), [self.ftir, self.nmr])
        self.client.post(self.url(), {"instrument": self.ftir.pk, "action": "revoke"})

        self.assertRedirects(assigned, self.url(), fetch_redirect_response=False)
        self.assertCountEqual(self.student.instruments.all(), [self.nmr])

    def test_assigning_without_choosing_an_instrument_changes_nothing(self):
        response = self.client.post(
            self.url(), {"instrument": "", "action": "assign"}, follow=True
        )

        self.assertContains(response, "Choose an instrument first.")
        self.assertFalse(self.student.instruments.exists())


class SeedFromBookingsTestCase(RequestBuilderMixin, TestCase):
    """Existing students keep the instruments they were approved for."""

    def seed(self):
        importlib.import_module(
            "booking_portal.migrations.0094_seed_student_instruments"
        ).assign_approved_instruments(apps, None)

    def test_only_an_approved_request_assigns_an_instrument(self):
        self.build_portal_fixtures()
        self.make_request(StudentRequest.APPROVED, date=timezone.localdate())
        for name, status in (
            ("NMR", StudentRequest.WAITING_FOR_FACULTY),
            ("XPS", StudentRequest.WAITING_FOR_LAB_ASST),
            ("BET", StudentRequest.REJECTED),
            ("AAS", StudentRequest.CANCELLED),
        ):
            self.make_request(
                status,
                date=timezone.localdate(),
                instrument=InstrumentFactory(name=name),
            )

        self.seed()
        self.seed()

        self.assertCountEqual(self.student.instruments.all(), [self.instrument])

    def test_a_single_booking_over_a_year_old_has_lapsed(self):
        self.build_portal_fixtures()
        long_ago = timezone.localdate() - datetime.timedelta(days=400)
        lapsed, regular = InstrumentFactory(name="NMR"), InstrumentFactory(name="XPS")
        self.make_request(StudentRequest.APPROVED, date=timezone.localdate())
        self.make_request(StudentRequest.APPROVED, date=long_ago, instrument=lapsed)
        for _ in range(2):
            self.make_request(
                StudentRequest.APPROVED, date=long_ago, instrument=regular
            )

        self.seed()

        self.assertCountEqual(
            self.student.instruments.all(), [self.instrument, regular]
        )


class NewStudentTestCase(TestCase):
    def test_a_new_student_has_no_instruments_and_is_told_why(self):
        InstrumentFactory(name="FTIR")
        records = csv.DictReader(
            io.StringIO(
                "name,email,password,supervisor\n"
                f"Asha Rao,asha@example.com,,{FacultyFactory().email}\n"
            )
        )

        StudentAdmin(Student, admin.site).create_users(
            Student, records, notify_user=True
        )

        student = Student.objects.get(email="asha@example.com")
        self.assertFalse(student.instruments.exists())
        email = EmailModel.objects.get(receiver=student.email)
        for body in (email.text, email.text_html):
            self.assertIn("Your account starts with no instruments assigned", body)
            self.assertNotIn("start booking slots right away", body)
