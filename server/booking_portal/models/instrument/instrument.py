import csv
import datetime

from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver

from ..request import Request
from ..slot import Slot


class InstrumentManager(models.Manager):
    def export_instrument_usage_report(self, file, instruments, start_date, end_date):
        headers = (
            "Instrument Name",
            "Approved Bookings",
            "Total Utilisation (hours:minutes)",
        )
        writer = csv.DictWriter(file, headers)
        writer.writeheader()

        for instr in instruments:
            requests = Request.objects.filter(
                instrument=instr,
                slot__date__gte=start_date,
                slot__date__lte=end_date,
                status=Request.APPROVED,
            ).select_related("slot")
            approved_count = requests.count()

            # Calculate the total utilisation for the instrument
            utilisation = datetime.timedelta()
            for request in requests:
                print(request.slot.duration)
                utilisation += request.slot.duration
            util_hours, remainder = divmod(utilisation.total_seconds(), 3600)
            util_minutes, _ = divmod(remainder, 60)

            row = {
                "Instrument Name": instr.name,
                "Approved Bookings": approved_count,
                "Total Utilisation (hours:minutes)": "%s:%s"
                % (int(util_hours), int(util_minutes)),
            }
            writer.writerow(row)


class Instrument(models.Model):
    name = models.CharField(max_length=50, unique=True, null=False)
    desc = models.CharField(max_length=200, null=True)
    status = models.BooleanField(
        help_text="'No' will cancel all pending requests and slots for this machine",
        verbose_name="Available for Booking?",
        default=True,
    )
    cost_per_sample = models.IntegerField(default=0)

    objects: InstrumentManager = InstrumentManager()

    @property
    def short_id(self):
        return self.name

    def __str__(self):
        return f"{self.name}"

    class Meta:
        ordering = [
            "name",
        ]


@receiver(post_save, sender=Instrument)
def handle_requests(sender, instance, **kwargs):
    if instance.status:
        for slot in Slot.objects.filter(
            instrument=instance,
            date__gte=datetime.datetime.today(),
            status=Slot.STATUS_4,
        ):
            slot.status = Slot.STATUS_1
            slot.save()
    else:
        slot_objects = Slot.objects.filter(
            ~(Q(status=Slot.STATUS_4)),
            instrument=instance,
            date__gte=datetime.datetime.today(),
        )

        req_objects = Request.objects.filter(
            ~(Q(status=Request.REJECTED) | Q(status=Request.CANCELLED)),
            instrument=instance,
            slot__date__gte=datetime.datetime.today(),
        )

        for slot in slot_objects:
            slot.status = Slot.STATUS_4
            slot.save()

        for req in req_objects:
            req.status = Request.CANCELLED

            previous_remarks = req.content_object.lab_assistant_remarks
            new_remarks = (
                "This slot has been cancelled due to technical/maintainence reasons."
            )
            if previous_remarks is not None:
                new_remarks = previous_remarks + "\n" + new_remarks

            req.content_object.lab_assistant_remarks = new_remarks
            req.content_object.save()
            req.save()
