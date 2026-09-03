import datetime
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.messages import get_messages
from django.test import Client, TestCase
from django.urls import reverse

from ..factories import InstrumentFactory, LabAssistantFactory
from ..forms import BulkCreateSlotsForm
from ..models import Slot

# A fixed working hour rather than the wall clock: these tests add an hour to
# this time to get an end time, so a run late in the evening would ask for a
# window ending the next day, which the form refuses. The date stays today,
# because the form refuses a start date in the past, rolled off Sunday, which
# slot generation skips.
_VALID_DATE_TIME = datetime.datetime.combine(datetime.date.today(), datetime.time(9))
if _VALID_DATE_TIME.date().weekday() == 6:
    _VALID_DATE_TIME += timedelta(days=1)


class OverlappingSlotTestCase(TestCase):
    def setUp(self):
        self.now = _VALID_DATE_TIME
        instr = InstrumentFactory()
        self.slot = Slot.objects.create(
            instrument=instr,
            status=Slot.STATUS_1,
            date=datetime.date.today(),
            start_time=self.now,
            end_time=self.now + timedelta(minutes=30),
        )

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
        self.form = BulkCreateSlotsForm(
            data={
                "instrument": str(self.instr.pk),
                "start_date": str(datetime.date.today()),
                "start_time": str(self.now.time()),
                "end_time": str((self.now + timedelta(minutes=30)).time()),
                "slot_duration": "30",
                "for_the_next": "7",
            }
        )

    def test_invalid_duration(self):
        form = self.form
        form.data["slot_duration"] = "0"

        self.assertIn("slot_duration", form.errors)
        self.assertEqual(
            form.errors["slot_duration"],
            ["The duration in minutes must be a positive integer."],
        )

    def test_start_time_after_end_time(self):
        form = self.form
        form.data["start_time"] = str((self.now + timedelta(minutes=31)).time())

        self.assertIn("start_time", form.errors)
        self.assertEqual(
            form.errors["start_time"], ["Start time cannot be after end time."]
        )

    def test_start_date_before_today(self):
        form = self.form
        form.data["start_date"] = str(
            (datetime.datetime.now() - timedelta(days=1)).date()
        )

        self.assertIn("start_date", form.errors)
        self.assertEqual(
            form.errors["start_date"], ["Start date cannot be before today."]
        )

    def test_duration_gives_whole_number_of_slots(self):
        form = self.form
        form.data["slot_duration"] = "31"
        self.assertIn(
            "Cannot create whole number of slots between specified start and "
            "end time with the given duration.",
            form.non_field_errors(),
        )

    def test_valid_form(self):
        self.assertTrue(self.form.is_valid())


class BulkCreateSlotsTestCase(TestCase):
    SLOTS_A_DAY = 6  # a one hour window cut into ten minute slots

    @classmethod
    def setUpTestData(cls):
        cls.instr = InstrumentFactory()

    def setUp(self):
        self.user = LabAssistantFactory()
        self.client = Client()
        self.client.force_login(self.user)
        self.now = _VALID_DATE_TIME

    def create_slots(self, day_count):
        """Ask the admin form for slots the way the lab assistant does."""
        return self.client.post(
            reverse("admin:booking_portal_slot_bulk-slots_create"),
            {
                "instrument": self.instr.pk,
                "start_date": self.now.date(),
                "start_time": self.now.time(),
                "end_time": (self.now + timedelta(minutes=60)).time(),
                "slot_duration": "10",
                "for_the_next": day_count,
            },
        )

    def fill_the_first_day(self):
        Slot.objects.bulk_create_slots(
            instr=self.instr,
            start_date=self.now.date(),
            start_time=self.now.time(),
            end_time=(self.now + timedelta(minutes=60)).time(),
            duration=timedelta(minutes=10),
            day_count=1,
        )

    def assertReported(self, response, message, level):
        # The view only reports once it has accepted the form: a rejected one
        # re-renders the page and says nothing, so assert the redirect first or
        # a validation failure shows up as an empty message list.
        self.assertEqual(response.status_code, 302)
        self.assertIn(
            (message, settings.MESSAGE_TAGS[level]),
            [(m.message, m.level_tag) for m in get_messages(response.wsgi_request)],
        )

    def test_successful_slot_creation(self):
        response = self.create_slots(day_count=1)

        self.assertReported(
            response, "All slots were created successfully.", messages.SUCCESS
        )
        self.assertEqual(Slot.objects.count(), self.SLOTS_A_DAY)

    def test_partially_successful_slot_creation(self):
        self.fill_the_first_day()

        response = self.create_slots(day_count=7)

        # a week holds one Sunday, which is skipped, and day one already clashes
        expected_total = 36
        expected_created = expected_total - self.SLOTS_A_DAY
        self.assertReported(
            response,
            f"{expected_created} out of {expected_total} slots created. Some slots "
            f"may not have been created due to clashes with existing slots.",
            messages.WARNING,
        )
        # the clashing day was left alone rather than doubled up
        self.assertEqual(Slot.objects.count(), expected_total)

    def test_unsuccessful_slot_creation(self):
        self.fill_the_first_day()

        response = self.create_slots(day_count=1)

        self.assertReported(
            response,
            f"0 out of {self.SLOTS_A_DAY} slots created. Some slots may not have "
            f"been created due to clashes with existing slots.",
            messages.WARNING,
        )
        self.assertEqual(Slot.objects.count(), self.SLOTS_A_DAY)

    def test_a_window_that_ends_before_it_starts_creates_nothing(self):
        response = self.client.post(
            reverse("admin:booking_portal_slot_bulk-slots_create"),
            {
                "instrument": self.instr.pk,
                "start_date": self.now.date(),
                "start_time": datetime.time(23, 30),
                "end_time": datetime.time(0, 30),
                "slot_duration": "10",
                "for_the_next": 1,
            },
        )

        # the form comes back for correction instead of redirecting, and the
        # lab assistant is told nothing was done
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Start time cannot be after end time.")
        self.assertEqual(list(get_messages(response.wsgi_request)), [])
        self.assertEqual(Slot.objects.count(), 0)
