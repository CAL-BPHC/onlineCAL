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
    FacultyFactory,
    InstrumentFactory,
    LabAssistantFactory,
    StudentFactory,
)
from ..models import Department, EmailModel, Slot, Student, StudentRequest
from .test_portal_filters import RequestBuilderMixin

ACCESS_URL = "/lab-assistant/instrument-access"


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
    """Lab assistants assign a student an instrument after training, or revoke it."""

    def setUp(self):
        self.student = StudentFactory(name="Asha Rao")
        self.ftir = InstrumentFactory(name="FTIR")
        self.nmr = InstrumentFactory(name="NMR")
        self.client = Client()
        self.client.force_login(LabAssistantFactory())

    def url(self):
        return f"{ACCESS_URL}/{self.student.pk}"

    def test_only_lab_assistants_can_use_it(self):
        department = Department.objects.create(email="d@example.com", name="chem")
        for user in (self.student, self.student.supervisor, department):
            with self.subTest(role=user.role):
                self.client.force_login(user)

                for url in (ACCESS_URL, self.url()):
                    self.assertEqual(self.client.get(url).status_code, 302)
                self.client.post(
                    self.url(), {"instrument": self.ftir.pk, "action": "assign"}
                )

        self.assertFalse(self.student.instruments.exists())

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

    def test_the_page_offers_to_revoke_what_is_assigned_and_assign_the_rest(self):
        self.student.instruments.add(self.ftir)

        body = self.client.get(self.url()).content.decode()

        self.assertIn("Can book (1)", body)
        self.assertIn(f'<option value="{self.nmr.pk}">NMR</option>', body)
        self.assertNotIn(f'<option value="{self.ftir.pk}">', body)

    def test_assigning_and_revoking_change_one_instrument_each(self):
        # assigned by another lab assistant since this page was opened
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
    """Existing students keep the instruments they already book."""

    def test_each_instrument_booked_is_assigned_unless_it_never_took_place(self):
        seed = importlib.import_module(
            "booking_portal.migrations.0094_seed_student_instruments"
        )
        self.build_portal_fixtures()
        pending, refused = InstrumentFactory(name="NMR"), InstrumentFactory(name="XPS")
        self.make_request(StudentRequest.APPROVED)
        self.make_request(StudentRequest.APPROVED)
        self.make_request(StudentRequest.WAITING_FOR_FACULTY, instrument=pending)
        self.make_request(StudentRequest.REJECTED, instrument=refused)
        self.make_request(StudentRequest.CANCELLED, instrument=refused)

        seed.assign_booked_instruments(apps, None)
        seed.assign_booked_instruments(apps, None)

        self.assertCountEqual(
            self.student.instruments.all(), [self.instrument, pending]
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
