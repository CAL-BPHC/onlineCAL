import random
from typing import cast

import booking_portal.models.instrument
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, transaction
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils.timezone import now

from .email import EmailModel
from .instrument.requests import UserDetail
from .slot import Slot
from .user import Faculty, LabAssistant


class FacultyRequestManager(models.Manager):
    def create_request(self, form_instance, slot_id, faculty):
        with transaction.atomic():
            slot, instr = Slot.objects.get_instr_from_slot_id(slot_id, True)
            if not instr or not slot:
                raise ObjectDoesNotExist("Requested slot or instrument does not exist.")

            if not slot.is_available_for_booking():
                raise ValueError("Slot is not available for booking.")

            if FacultyRequest.objects.has_faculty_booked_upcoming_instrument_slot(
                instr, faculty
            ):
                raise ValueError("Upcoming slot for instrument already booked.")

            # mode_id = form_instance.cleaned_data.get("mode")
            # if not mode_id:
            #     raise ValueError("Mode is required for booking.")

            # mode = booking_portal.models.instrument.ModePricingRules.objects.get(
            #     id=mode_id
            # )
            mode_id = form_instance.cleaned_data.get("mode")
            mode = None
            if mode_id:
                mode = booking_portal.models.instrument.ModePricingRules.objects.get(
                    id=mode_id
                )
            # handle additional fields
            data_to_store = []
            cleaned_data = form_instance.cleaned_data
            Rules = booking_portal.models.instrument.AdditionalPricingRules
            for key, value in cleaned_data.items():
                if key.startswith("additional_charge_"):
                    charge_id = key.split("_")[-1]
                    # Additional charge selected
                    rule = Rules.objects.get(id=charge_id)
                    if isinstance(value, str):
                        # Handle choice field
                        data_to_store.append(
                            {**rule.__dict__, "selected_choice": value}
                        )
                    elif value:
                        if rule.rule_type == Rules.CONDITIONAL_FIELD:
                            data_to_store.append(
                                {
                                    **rule.__dict__,
                                    "conditional_quantity": cleaned_data[
                                        f"conditional_quantity_{charge_id}"
                                    ],
                                }
                            )
                        else:
                            data_to_store.append({**rule.__dict__})

            for val in data_to_store:
                del val["_state"]

            status = FacultyRequest.WAITING_FOR_LAB_ASST
            if form_instance.cleaned_data["needs_department_approval"]:
                status = FacultyRequest.WAITING_FOR_DEPARTMENT
            form_saved = form_instance.save()
            self.create(
                faculty=faculty,
                instrument=instr,
                slot=slot,
                status=status,
                lab_assistant=random.choice(
                    LabAssistant.objects.filter(is_active=True)
                ),
                content_object=form_saved,
                needs_department_approval=form_instance.cleaned_data[
                    "needs_department_approval"
                ],
                mode_description=mode.description if mode else "",
                mode_cost=mode.cost if mode else 0,
                mode_rule_type=mode.rule_type if mode else "",
                mode_time_in_minutes=mode.time_in_minutes if mode else 0,
                additional_charges=data_to_store,
            )
            slot.update_status(Slot.STATUS_2)

    @staticmethod
    def has_faculty_booked_upcoming_instrument_slot(instr, faculty, date=now().date()):
        """Check if a faculty has booked an upcoming slot for an instrument"""
        return FacultyRequest.objects.filter(
            ~(
                Q(status=FacultyRequest.REJECTED)
                | Q(status=FacultyRequest.CANCELLED)
                | Q(status=FacultyRequest.APPROVED)
            ),
            instrument=instr,
            faculty=faculty,
            slot__date__gte=date,
        ).exists()


class FacultyRequest(models.Model):
    WAITING_FOR_LAB_ASST = "R2"
    APPROVED = "R3"
    REJECTED = "R4"
    CANCELLED = "R5"
    WAITING_FOR_DEPARTMENT = "R6"

    STATUS_CHOICES = [
        (WAITING_FOR_LAB_ASST, "Waiting for lab assistant approval."),
        (APPROVED, "Approved"),
        (REJECTED, "Rejected"),
        (CANCELLED, "Cancelled"),
        (WAITING_FOR_DEPARTMENT, "Waiting for department approval"),
    ]

    objects: FacultyRequestManager = FacultyRequestManager()
    # this field is solely here to ease the union of the two models
    student = models.ForeignKey(
        "Student", on_delete=models.PROTECT, blank=True, null=True, default=None
    )
    faculty = models.ForeignKey(Faculty, on_delete=models.PROTECT)
    lab_assistant = models.ForeignKey(
        LabAssistant, on_delete=models.PROTECT, blank=True, null=True
    )
    instrument = models.ForeignKey("Instrument", on_delete=models.PROTECT)
    slot = models.ForeignKey(Slot, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    needs_department_approval = models.BooleanField(default=False)

    # need to know which mode the requested instrument has so we can calculate cost and have it for future reference
    mode_description = models.CharField(max_length=200)
    mode_cost = models.IntegerField()
    mode_rule_type = models.CharField(
        max_length=100,
    )
    mode_time_in_minutes = models.IntegerField(default=0)

    # to store the additional fields so we can calculate cost and have it for future reference
    additional_charges = models.JSONField(default=list)
    # To keep a reference of different form types
    # against a request
    content_type = models.ForeignKey(
        ContentType, on_delete=models.PROTECT, blank=True, null=True
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    @property
    def total_cost(self):
        total_cost = 0

        duration = self.slot.duration
        duration_in_minutes = duration.total_seconds() / 60

        num_samples = cast(UserDetail, self.content_object).number_of_samples

        if (
            self.mode_rule_type
            == booking_portal.models.instrument.ModePricingRules.FLAT
        ):
            total_cost += self.mode_cost
        elif (
            self.mode_rule_type
            == booking_portal.models.instrument.ModePricingRules.PER_SAMPLE
        ):
            total_cost += self.mode_cost * num_samples
        elif (
            self.mode_rule_type
            == booking_portal.models.instrument.ModePricingRules.PER_TIME_UNIT
        ):
            total_cost += self.mode_cost * (
                duration_in_minutes / self.mode_time_in_minutes
            )

        # additional costs
        Rule = booking_portal.models.instrument.AdditionalPricingRules
        for charge in self.additional_charges:
            if charge["rule_type"] == Rule.FLAT:
                total_cost += charge["cost"]
            elif charge["rule_type"] == Rule.PER_SAMPLE:
                total_cost += charge["cost"] * num_samples
            elif charge["rule_type"] == Rule.PER_TIME_UNIT:
                total_cost += charge["cost"] * (
                    duration_in_minutes / charge["time_in_minutes"]
                )
            elif charge["rule_type"] == Rule.CHOICE_FIELD:
                for choice in charge["choices"]:
                    if charge["selected_choice"] == choice["value"]:
                        total_cost += choice["cost"] * num_samples
                        break
            elif charge["rule_type"] == Rule.CONDITIONAL_FIELD:
                if charge["conditional_quantity"]:
                    total_cost += (
                        charge["conditional_cost"] * charge["conditional_quantity"]
                    )
        return total_cost

    def update_status(self, status):
        assert status in (
            FacultyRequest.WAITING_FOR_LAB_ASST,
            FacultyRequest.APPROVED,
            FacultyRequest.REJECTED,
            FacultyRequest.CANCELLED,
        )
        self.status = status
        self.save(update_fields=["status"])

    def __str__(self):
        return "Request: {}".format(self.slot)


@receiver(signal=post_save, sender=FacultyRequest)
def send_email_after_save(sender, instance, **kwargs):
    slot = Slot.objects.get(id=instance.slot.id)
    if instance.status == FacultyRequest.WAITING_FOR_DEPARTMENT:
        subject = "Waiting for Department Approval"
        text = render_to_string(
            "email/department_pending.txt",
            {
                "recipient_name": instance.faculty.department.name,
                "student_name": instance.faculty.name,
                "instrument_name": instance.instrument.name,
                "slot": instance.slot.description,
                "faculty_name": instance.faculty.name,
            },
        )
        text_html = render_to_string(
            "email/department_pending.html",
            {
                "recipient_name": instance.faculty.department.name,
                "student_name": instance.faculty.name,
                "instrument_name": instance.instrument.name,
                "slot": instance.slot.description,
                "faculty_name": instance.faculty.name,
            },
        )
        instance.faculty.department.send_email(subject, text, text_html)
    elif instance.status == FacultyRequest.WAITING_FOR_LAB_ASST:
        subject = "Waiting for Lab Assistant Approval"
        text = render_to_string(
            "email/lab_assistant_pending.txt",
            {
                "recipient_name": "Lab Technicians",
                "student_name": instance.faculty.name,
                "instrument_name": instance.instrument.name,
                "faculty_name": instance.faculty.name,
                "slot": instance.slot.description,
            },
        )
        text_html = render_to_string(
            "email/lab_assistant_pending.html",
            {
                "recipient_name": "Lab Technicians",
                "student_name": instance.faculty.name,
                "instrument_name": instance.instrument.name,
                "faculty_name": instance.faculty.name,
                "slot": instance.slot.description,
            },
        )
        # instead of sending mail to a lab assistant send it to the common email
        # instance.lab_assistant.send_email(subject, text, text_html)

        # Don't send emails as they are too many, and lab assts check the portal for pending requests
        # EmailModel(
        #     receiver="cal@hyderabad.bits-pilani.ac.in",
        #     text=text,
        #     text_html=text_html,
        #     subject=subject,
        #     sent=False,
        # ).save()
    elif instance.status == FacultyRequest.APPROVED:
        slot.update_status(Slot.STATUS_3)
        subject = "Lab Booking Approved"
        text = render_to_string(
            "email/student_accepted.txt",
            {
                "recipient_name": instance.faculty.name,
                "slot": instance.slot.description,
            },
        )
        text_html = render_to_string(
            "email/student_accepted.html",
            {
                "recipient_name": instance.faculty.name,
                "slot": instance.slot.description,
            },
        )
        instance.faculty.send_email(subject, text, text_html)
    elif (
        instance.status == FacultyRequest.REJECTED
        or instance.status == FacultyRequest.CANCELLED
    ):
        if instance.status == FacultyRequest.REJECTED:
            slot.update_status(Slot.STATUS_1)
            subject = "Lab Booking Rejected"
        else:
            subject = "Lab Booking Cancelled"
        text = render_to_string(
            "email/student_rejected.txt",
            {
                "recipient_name": instance.faculty.name,
                "slot": instance.slot.description,
                "faculty_remarks": instance.content_object.faculty_remarks,
                "lab_assistant_remarks": instance.content_object.lab_assistant_remarks,
            },
        )
        text_html = render_to_string(
            "email/student_rejected.html",
            {
                "recipient_name": instance.faculty.name,
                "slot": instance.slot.description,
                "faculty_remarks": instance.content_object.faculty_remarks,
                "lab_assistant_remarks": instance.content_object.lab_assistant_remarks,
            },
        )
        instance.faculty.send_email(subject, text, text_html)
