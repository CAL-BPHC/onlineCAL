import datetime
from datetime import timedelta

from django.conf import settings
from django.contrib.messages import get_messages
from django.contrib import messages
from django.test import Client
from django.test import TestCase
from django.urls import reverse

from ..factories import InstrumentFactory, LabAssistantFactory
from ..forms import BulkCreateSlotsForm
from ..models import Slot

# A valid date time will not fall on Sunday
_VALID_DATE_TIME = datetime.datetime.now()
if _VALID_DATE_TIME.date().weekday() == 6:
    _VALID_DATE_TIME += timedelta(days=1)


class OverlappingSlotTestCase(TestCase):
    def setUp(self):
        self.now = _VALID_DATE_TIME
        instr = InstrumentFactory()
        self.slot = Slot.objects.create(instrument=instr, status=Slot.STATUS_1, date=datetime.date.today(),
                                        start_time=self.now, end_time=self.now + timedelta(minutes=30))

    def test_when_new_completely_inside_old(self):
        slot = self.slot
        now = self.now
        manager = Slot.objects

        # completely equivalent or inside existing slot
        slot.start_time = now + timedelta(minutes=0)
        slot.end_time = now + timedelta(minutes=29)
        self.assertTrue(manager.is_slot_overlapping(slot))

        # begins before existing slot ends and ends after
        slot.start_time = now + timedelta(minutes=1)
        slot.end_time = now + timedelta(minutes=31)
        self.assertTrue(manager.is_slot_overlapping(slot))

        # begins before existing slot begins and ends after
        slot.start_time = now - timedelta(minutes=1)
        slot.end_time = now + timedelta(minutes=1)
        self.assertTrue(manager.is_slot_overlapping(slot))

        # subsumes or equivalent to existing slot
        slot.start_time = now - timedelta(minutes=0)
        slot.end_time = now + timedelta(minutes=31)
        self.assertTrue(manager.is_slot_overlapping(slot))

        # perfect slot
        slot.start_time = now + timedelta(minutes=30)
        slot.end_time = now + timedelta(minutes=31)
        self.assertFalse(manager.is_slot_overlapping(slot))

    def test_when_old_start_time_between_new_times(self):
        # new.start_time < old.start_time < new.end_time
        self.slot.start_time = self.now + timedelta(minutes=1)
        self.slot.end_time = self.now + timedelta(minutes=31)
        self.assertTrue(Slot.objects.is_slot_overlapping(self.slot))

    def test_when_old_end_time_within_new_times(self):
        # new.start_time < old.end_time < new.end_time
        self.slot.start_time = self.now - timedelta(minutes=1)
        self.slot.end_time = self.now + timedelta(minutes=1)
        self.assertTrue(Slot.objects.is_slot_overlapping(self.slot))

    def test_when_old_completley_inside_new(self):
        # new.start_time <= old.start_time < old.end_time <= new.end_time
        self.slot.start_time = self.now - timedelta(minutes=0)
        self.slot.end_time = self.now + timedelta(minutes=31)
        self.assertTrue(Slot.objects.is_slot_overlapping(self.slot))

    def test_when_same_time_for_old_and_new(self):
        # new.start_time == old.start_Time && old.end_time == new.end_time
        new = self.slot
        new.pk = None
        self.assertTrue(Slot.objects.is_slot_overlapping(self.slot))

    def test_valid_slot(self):
        self.slot.start_time = self.now + timedelta(minutes=30)
        self.slot.end_time = self.now + timedelta(minutes=31)
        self.assertFalse(Slot.objects.is_slot_overlapping(self.slot))


class BulkCreateSlotsFormTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.instr = InstrumentFactory()

    def setUp(self):
        # We create a base valid form. Each test will modify and make it invalid.
        self.now = _VALID_DATE_TIME
        self.form = BulkCreateSlotsForm(data={
            'instrument': str(self.instr.pk),
            'start_date': str(datetime.date.today()),
            'start_time': str(self.now.time()),
            'end_time': str((self.now + timedelta(minutes=30)).time()),
            'slot_duration': "30",
            'for_the_next': "7",
        })

    def test_invalid_duration(self):
        form = self.form
        form.data['slot_duration'] = "0"

        self.assertIn('slot_duration', form.errors)
        self.assertEqual(
            form.errors['slot_duration'], [
                "The duration in minutes must be a positive integer."]
        )

    def test_start_time_after_end_time(self):
        form = self.form
        form.data['start_time'] = str(
            (self.now + timedelta(minutes=31)).time())

        self.assertIn('start_time', form.errors)
        self.assertEqual(
            form.errors['start_time'], ["Start time cannot be after end time."]
        )

    def test_start_date_before_today(self):
        form = self.form
        form.data['start_date'] = str(
            (datetime.datetime.now() - timedelta(days=1)).date())

        self.assertIn('start_date', form.errors)
        self.assertEqual(
            form.errors['start_date'], ["Start date cannot be before today."]
        )

    def test_duration_gives_whole_number_of_slots(self):
        form = self.form
        form.data['slot_duration'] = "31"
        self.assertIn(
            "Cannot create whole number of slots between specified start and "
            "end time with the given duration.",
            form.non_field_errors(),
        )

    def test_valid_form(self):
        self.assertTrue(self.form.is_valid())


class BulkCreateSlotsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.instr = InstrumentFactory()

    def setUp(self):
        self.user = LabAssistantFactory()
        self.client = Client()
        self.client.force_login(self.user)
        self.now = _VALID_DATE_TIME

    def test_successful_slot_creation(self):
        url = reverse('admin:booking_portal_slot_bulk-slots_create')
        # Set a date that is not Sunday
        response = self.client.post(
            url,
            {
                'instrument': self.instr.pk,
                'start_date': self.now.date(),
                'start_time': self.now.time(),
                'end_time': (self.now + timedelta(minutes=60)).time(),
                'slot_duration': '10',
                'for_the_next': 1,
            }
        )

        message_list = [(x.message, x.level_tag)
                        for x in get_messages(response.wsgi_request)]
        self.assertIn(
            ("All slots were created successfully.",
             settings.MESSAGE_TAGS[messages.SUCCESS]),
            message_list,
        )

    def test_partially_successful_slot_creation(self):
        Slot.objects.bulk_create_slots(
            instr=self.instr,
            start_date=self.now.date(),
            start_time=self.now.time(),
            end_time=(self.now + timedelta(minutes=60)).time(),
            duration=timedelta(minutes=10),
            day_count=1,
        )

        # Now try creating partially overlapping slots
        url = reverse('admin:booking_portal_slot_bulk-slots_create')
        response = self.client.post(
            url,
            {
                'instrument': self.instr.pk,
                'start_date': self.now.date(),
                'start_time': self.now.time(),
                'end_time': (self.now + timedelta(minutes=60)).time(),
                'slot_duration': '10',
                'for_the_next': 7,
            }
        )
        # 6 slots a day for 6 days (no slots on Sunday)
        expected_total_slots = 36
        expected_created_slots = 30  # everything clashes on day 1
        expected_message = (f"{expected_created_slots} out of {expected_total_slots} slots created. Some slots may not "
                            f"have been created due to clashes with existing slots.")

        message_list = [(x.message, x.level_tag)
                        for x in get_messages(response.wsgi_request)]
        self.assertIn(
            (expected_message, settings.MESSAGE_TAGS[messages.WARNING]),
            message_list,
        )

    def test_unsuccessful_slot_creation(self):
        Slot.objects.bulk_create_slots(
            instr=self.instr,
            start_date=self.now.date(),
            start_time=self.now.time(),
            end_time=(self.now + timedelta(minutes=60)).time(),
            duration=timedelta(minutes=10),
            day_count=1,
        )

        # Now try to create overlapping slots
        url = reverse('admin:booking_portal_slot_bulk-slots_create')
        response = self.client.post(
            url,
            {
                'instrument': self.instr.pk,
                'start_date': self.now.date(),
                'start_time': self.now.time(),
                'end_time': (self.now + timedelta(minutes=60)).time(),
                'slot_duration': '10',
                'for_the_next': 1,
            }
        )
        expected_total_slots = 6
        expected_created_slots = 0
        expected_message = (f"{expected_created_slots} out of {expected_total_slots} slots created. Some slots may not "
                            f"have been created due to clashes with existing slots.")

        message_list = [(x.message, x.level_tag)
                        for x in get_messages(response.wsgi_request)]
        self.assertIn(
            (expected_message, settings.MESSAGE_TAGS[messages.WARNING]),
            message_list,
        )
