from typing import cast

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, transaction
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils.timezone import now

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

            form_saved = form_instance.save()
            self.create(
                faculty=faculty,
                instrument=instr,
                slot=slot,
                status=FacultyRequest.WAITING_FOR_LAB_ASST,
                content_object=form_saved,
                needs_department_approval=form_instance.cleaned_data[
                    "needs_department_approval"
                ],
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

    faculty = models.ForeignKey(Faculty, on_delete=models.PROTECT)
    lab_assistant = models.ForeignKey(
        LabAssistant, on_delete=models.PROTECT, blank=True, null=True
    )
    instrument = models.ForeignKey("Instrument", on_delete=models.PROTECT)
    slot = models.ForeignKey(Slot, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    needs_department_approval = models.BooleanField(default=False)

    # To keep a reference of different form types
    # against a request
    content_type = models.ForeignKey(
        ContentType, on_delete=models.PROTECT, blank=True, null=True
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    @property
    def total_cost(self):
        return (
            self.instrument.cost_per_sample
            * cast(UserDetail, self.content_object).number_of_samples
        )

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


# @receiver(signal=post_save, sender=FacultyRequest)
# def send_email_after_save(sender, instance, **kwargs):
#     slot = Slot.objects.get(id=instance.slot.id)
#     if instance.status == FacultyRequest.WAITING_FOR_DEPARTMENT:
#         subject = "Waiting for Department Approval"
#         text = render_to_string(
#             "email/department_pending.txt",
#             {
#                 "receipent_name": instance.faculty.department.name,
#                 "student_name": instance.student.name,
#                 "instrument_name": instance.instrument.name,
#                 "slot": instance.slot.description,
#                 "faculty_name": instance.faculty.name,
#             },
#         )
#         text_html = render_to_string(
#             "email/department_pending.html",
#             {
#                 "receipent_name": instance.faculty.department.name,
#                 "student_name": instance.student.name,
#                 "instrument_name": instance.instrument.name,
#                 "slot": instance.slot.description,
#                 "faculty_name": instance.faculty.name,
#             },
#         )
#         instance.faculty.department.send_email(subject, text, text_html)
#     elif instance.status == FacultyRequest.WAITING_FOR_LAB_ASST:
#         subject = "Waiting for Lab Assistant Approval"
#         text = render_to_string(
#             "email/lab_assistant_pending.txt",
#             {
#                 "receipent_name": instance.lab_assistant.name,
#                 "student_name": instance.student.name,
#                 "instrument_name": instance.instrument.name,
#                 "faculty_name": instance.faculty.name,
#                 "slot": instance.slot.description,
#             },
#         )
#         text_html = render_to_string(
#             "email/lab_assistant_pending.html",
#             {
#                 "receipent_name": instance.lab_assistant.name,
#                 "student_name": instance.student.name,
#                 "instrument_name": instance.instrument.name,
#                 "faculty_name": instance.faculty.name,
#                 "slot": instance.slot.description,
#             },
#         )
#         instance.lab_assistant.send_email(subject, text, text_html)
#     elif instance.status == FacultyRequest.APPROVED:
#         slot.update_status(Slot.STATUS_3)
#         subject = "Lab Booking Approved"
#         text = render_to_string(
#             "email/student_accepted.txt",
#             {
#                 "receipent_name": instance.student.name,
#                 "slot": instance.slot.description,
#             },
#         )
#         text_html = render_to_string(
#             "email/student_accepted.html",
#             {
#                 "receipent_name": instance.student.name,
#                 "slot": instance.slot.description,
#             },
#         )
#         instance.student.send_email(subject, text, text_html)
#     elif (
#         instance.status == FacultyRequest.REJECTED
#         or instance.status == FacultyRequest.CANCELLED
#     ):
#         if instance.status == FacultyRequest.REJECTED:
#             slot.update_status(Slot.STATUS_1)
#             subject = "Lab Booking Rejected"
#         else:
#             subject = "Lab Booking Cancelled"
#         text = render_to_string(
#             "email/student_rejected.txt",
#             {
#                 "receipent_name": instance.student.name,
#                 "slot": instance.slot.description,
#                 "faculty_remarks": instance.content_object.faculty_remarks,
#                 "lab_assistant_remarks": instance.content_object.lab_assistant_remarks,
#             },
#         )
#         text_html = render_to_string(
#             "email/student_rejected.html",
#             {
#                 "receipent_name": instance.student.name,
#                 "slot": instance.slot.description,
#                 "faculty_remarks": instance.content_object.faculty_remarks,
#                 "lab_assistant_remarks": instance.content_object.lab_assistant_remarks,
#             },
#         )
#         instance.student.send_email(subject, text, text_html)
