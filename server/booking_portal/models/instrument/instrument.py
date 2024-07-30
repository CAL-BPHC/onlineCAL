import csv
import datetime

from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver

from ..request import StudentRequest
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
            requests = StudentRequest.objects.filter(
                instrument=instr,
                slot__date__gte=start_date,
                slot__date__lte=end_date,
                status=StudentRequest.APPROVED,
            ).select_related("slot")
            approved_count = requests.count()

            # Calculate the total utilisation for the instrument
            utilisation = datetime.timedelta()
            for request in requests:
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

        req_objects = StudentRequest.objects.filter(
            ~(Q(status=StudentRequest.REJECTED) | Q(status=StudentRequest.CANCELLED)),
            instrument=instance,
            slot__date__gte=datetime.datetime.today(),
        )

        for slot in slot_objects:
            slot.status = Slot.STATUS_4
            slot.save()

        for req in req_objects:
            req.status = StudentRequest.CANCELLED

            previous_remarks = req.content_object.lab_assistant_remarks
            new_remarks = (
                "This slot has been cancelled due to technical/maintainence reasons."
            )
            if previous_remarks is not None:
                new_remarks = previous_remarks + "\n" + new_remarks

            req.content_object.lab_assistant_remarks = new_remarks
            req.content_object.save()
            req.save()


class ModePricingRules(models.Model):
    FLAT = "FLAT"
    PER_SAMPLE = "PER_SAMPLE"
    PER_TIME_UNIT = "PER_TIME_UNIT"

    RULE_TYPE_CHOICES = [
        (FLAT, "Flat Charge"),
        (PER_SAMPLE, "Per Sample Charge"),
        (PER_TIME_UNIT, "Per Time Unit Charge"),
    ]
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE)
    rule_type = models.CharField(max_length=100, choices=RULE_TYPE_CHOICES)
    description = models.CharField(max_length=200, null=True, blank=True)

    cost = models.IntegerField(default=0, null=True, blank=True)
    time_in_minutes = models.IntegerField(default=0, null=True, blank=True)

    @classmethod
    def get_mode_choices(cls, instr_id):
        modes = cls.objects.filter(instrument_id=instr_id)
        choices = []
        for mode in modes:
            if mode.rule_type == cls.FLAT:
                choices.append((mode.pk, f"{mode.description} - {mode.cost}"))
            elif mode.rule_type == cls.PER_SAMPLE:
                choices.append(
                    (mode.pk, f"{mode.description} - {mode.cost} per sample")
                )
            elif mode.rule_type == cls.PER_TIME_UNIT:
                choices.append(
                    (
                        mode.pk,
                        f"{mode.description} - {mode.cost} per {mode.time_in_minutes} minutes",
                    )
                )
        return choices

    def __str__(self):
        return f"{self.instrument.name} - {self.description}"


class AdditionalPricingRules(models.Model):
    FLAT = "FLAT"
    PER_SAMPLE = "PER_SAMPLE"
    PER_TIME_UNIT = "PER_TIME_UNIT"
    HELP_TEXT = "HELP_TEXT"
    CHOICE_FIELD = "CHOICE_FIELD"
    CONDITIONAL_FIELD = "CONDITIONAL_FIELD"

    RULE_TYPE_CHOICES = [
        (FLAT, "Flat Charge"),
        (PER_SAMPLE, "Per Sample Charge"),
        (PER_TIME_UNIT, "Per Time Unit Charge"),
        (HELP_TEXT, "Help Text"),
        (CHOICE_FIELD, "Choice Field"),
        (CONDITIONAL_FIELD, "Conditional Field"),
    ]

    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE)
    rule_type = models.CharField(max_length=100, choices=RULE_TYPE_CHOICES)
    description = models.CharField(max_length=200, null=True, blank=True)

    cost = models.IntegerField(default=0, null=True, blank=True)
    choices = models.JSONField(
        null=True, blank=True
    )  # Format: [{"value": "option1", "label": "Option 1", "cost": 10}, ...]
    time_in_minutes = models.IntegerField(default=0, null=True, blank=True)

    conditional_text = models.TextField(null=True, blank=True)
    conditional_cost = models.IntegerField(default=0, null=True, blank=True)

    def __str__(self):
        return f"{self.instrument.name} - {self.description}"
