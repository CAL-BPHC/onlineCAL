import datetime
from datetime import timedelta

from booking_portal.factories import (
    InstrumentFactory,
    LabAssistantFactory,
    StudentFactory,
)
from booking_portal.models import Slot, StudentRequest
from django.core.management import call_command
from django.test import Client, TestCase

# A valid date time will not fall on Sunday
_VALID_DATE_TIME = datetime.datetime.now()
if _VALID_DATE_TIME.date().weekday() == 6:
    _VALID_DATE_TIME += timedelta(days=1)


class SlotBookRequestTestCase(TestCase):
    def setUp(self):
        self.lab_assistant = LabAssistantFactory()
        self.student = StudentFactory()
        self.faculty = self.student.supervisor

        self.instrument = InstrumentFactory()
        self.slot = Slot.objects.create(
            instrument=self.instrument,
            status=Slot.STATUS_1,  # Empty
            date=_VALID_DATE_TIME.date(),
            start_time=_VALID_DATE_TIME.time(),
            end_time=(_VALID_DATE_TIME + timedelta(minutes=30)).time(),
        )

        self.client = Client()
        self.client.force_login(self.student)

    def test_student_booking_when_valid_request_exists(self):
        StudentRequest.objects.create(
            student=self.student,
            faculty=self.faculty,
            lab_assistant=self.lab_assistant,
            instrument=self.instrument,
            slot=self.slot,
            status=StudentRequest.WAITING_FOR_FACULTY,
            # There is no DB type constraint for `content_object`. Therefore,
            # we hack this field to be a Slot type. However, this should be
            # an instance of a model in models.instrument.requests
            content_object=self.slot,
        )

        self.assertTrue(
            StudentRequest.objects.has_student_booked_upcoming_instrument_slot(
                self.instrument, self.student, _VALID_DATE_TIME.date()
            )
        )

    def test_student_booking_when_no_request_exists(self):
        self.assertFalse(
            StudentRequest.objects.has_student_booked_upcoming_instrument_slot(
                self.instrument, self.student, _VALID_DATE_TIME.date()
            )
        )

    def test_student_booking_when_slot_not_unavailable(self):
        self.slot.status = Slot.STATUS_2
        self.slot.save()

        self.assertFalse(self.slot.is_available_for_booking())
