from __future__ import annotations

import calendar
import datetime
from typing import List, Tuple, TYPE_CHECKING

from django.db import models
from django.db.models import Q

if TYPE_CHECKING:
    from ..models.instrument import Instrument


class SlotManager(models.Manager):
    @staticmethod
    def get_valid_slot_days(
        start_date: datetime.date, day_count: int
    ) -> List[datetime.date]:
        # get the next `num_of_days`, skipping sundays
        next_days = [
            start_date + datetime.timedelta(days=var) for var in range(0, day_count)
        ]
        return [day for day in next_days if not day.weekday() == 6]

    def is_slot_overlapping(self, slot: Slot) -> bool:
        q = (
            Q(
                # Completely inside existing slot
                start_time__lte=slot.start_time,
                end_time__gte=slot.end_time,
            )
            | Q(
                # Begins before existing slot ends and ends after
                end_time__gt=slot.start_time,
                end_time__lt=slot.end_time,
            )
            | Q(
                # Ends after existing slot begins
                start_time__gt=slot.start_time,
                start_time__lt=slot.end_time,
            )
            | Q(
                # Subsumes existing slot
                start_time__gte=slot.start_time,
                end_time__lte=slot.end_time,
            )
        )

        return self.filter(q, instrument=slot.instrument, date=slot.date).exists()

    def bulk_create_slots(
        self,
        instr: Instrument,
        start_date: datetime.date,
        start_time: datetime.time,
        end_time: datetime.time,
        duration: datetime.timedelta,
        day_count: int,
    ) -> Tuple[int, int]:
        next_days = SlotManager.get_valid_slot_days(start_date, day_count)

        all_slots = {}
        for day in next_days:
            day_wise = []
            current = datetime.datetime.combine(day, start_time)
            end = datetime.datetime.combine(day, end_time)
            while current < end:
                day_wise.append(current.time())
                current = current + duration
            all_slots[day] = day_wise

        total_slots, slots_created = 0, 0
        slots = []
        for day, time_slots in all_slots.items():
            for slot_begin in time_slots:
                slot_end = (
                    datetime.datetime.combine(day, slot_begin) + duration
                ).time()
                total_slots += 1
                slot = Slot(
                    instrument=instr,
                    status=Slot.STATUS_1,
                    date=day,
                    start_time=slot_begin,
                    end_time=slot_end,
                )
                if not self.is_slot_overlapping(slot):
                    slots.append(slot)
                    slots_created += 1
        self.bulk_create(slots)
        return total_slots, slots_created

    def get_instr_from_slot_id(self, slot_id, lock=False):
        slot = self.select_related("instrument").filter(pk=slot_id)
        if lock:
            slot.select_for_update(of="self")
        if slot:
            return slot[0], slot[0].instrument
        return None, None


class Slot(models.Model):
    STATUS_1 = "S1"
    STATUS_2 = "S2"
    STATUS_3 = "S3"
    STATUS_4 = "S4"

    STATUS_CHOICES = [
        (STATUS_1, "Empty"),
        (STATUS_2, "In Process"),
        (STATUS_3, "Filled"),
        (STATUS_4, "Passed"),
    ]

    objects: SlotManager = SlotManager()

    ## TODO: Update Duration to TimeField
    instrument = models.ForeignKey("Instrument", on_delete=models.PROTECT)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    ## Remove date and time and combine it to DateTimeField

    def is_available_for_booking(self):
        return self.status == Slot.STATUS_1

    def update_status(self, status):
        assert status in (Slot.STATUS_1, Slot.STATUS_2, Slot.STATUS_3, Slot.STATUS_4)
        self.status = status
        self.save(update_fields=["status"])

    @property
    def duration(self):
        now_date = datetime.datetime.now().date()
        end_datetime = datetime.datetime.combine(now_date, self.end_time)
        start_datetime = datetime.datetime.combine(now_date, self.start_time)
        return end_datetime - start_datetime

    @property
    def duration_verbose(self):
        hours, reminder = divmod(self.duration.total_seconds(), 3600)
        minutes, seconds = divmod(reminder, 60)
        hours = f"{int(hours)} hr" if hours > 0 else ""
        minutes = f"{int(minutes)} min" if minutes > 0 else ""
        return " ".join((hours, minutes)).strip()

    @property
    def description(self):
        return "{} {} {} - {} to {} (Duration: {})".format(
            str(self.date.day),
            calendar.month_name[self.date.month],
            str(self.date.year),
            str(self.start_time),
            str(self.end_time),
            self.duration_verbose,
        )

    def __str__(self):
        return "{} : {}".format(self.instrument, self.description)
