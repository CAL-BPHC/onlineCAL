from django.db import models


class EmailModel(models.Model):
    FACULTY_APPROVAL = "faculty_approval"
    PENDING_BOOKING = "pending_booking"
    DEPARTMENT_APPROVAL = "department_approval"
    LAB_ASSISTANT_APPROVAL = "lab_assistant_approval"
    BOOKING_APPROVED = "booking_approved"
    BOOKING_REJECTED = "booking_rejected"
    BOOKING_CANCELLED = "booking_cancelled"
    NEW_ANNOUNCEMENT = "new_announcement"
    WELCOME = "welcome"
    OTHER = "other"

    EMAIL_TYPE_CHOICES = [
        (FACULTY_APPROVAL, "Waiting for Faculty Approval"),
        (PENDING_BOOKING, "Pending Lab Booking Request"),
        (DEPARTMENT_APPROVAL, "Waiting for Department Approval"),
        (LAB_ASSISTANT_APPROVAL, "Waiting for Lab Assistant Approval"),
        (BOOKING_APPROVED, "Lab Booking Approved"),
        (BOOKING_REJECTED, "Lab Booking Rejected"),
        (BOOKING_CANCELLED, "Lab Booking Cancelled"),
        (NEW_ANNOUNCEMENT, "New Announcement Created on CAL Portal"),
        (WELCOME, "Welcome to OnlineCAL!"),
        (OTHER, "Other"),
    ]

    @classmethod
    def get_subject_for_type(cls, email_type):
        """Get the human-readable subject for a given email type"""
        for choice_value, choice_label in cls.EMAIL_TYPE_CHOICES:
            if choice_value == email_type:
                return choice_label
        return "Other"

    receiver = models.EmailField(null=True, blank=False)
    date_time = models.DateTimeField(auto_now_add=True)
    text = models.TextField()
    text_html = models.TextField()
    subject = models.CharField(max_length=100, null=True)
    sent = models.BooleanField()
    email_type = models.CharField(
        max_length=50,
        choices=EMAIL_TYPE_CHOICES,
        default=OTHER,
        help_text="Type of email for categorization and filtering",
    )

    class Meta:
        verbose_name = "Email"
        verbose_name_plural = "Emails"
        default_related_name = "Emails"
        indexes = [models.Index(fields=["email_type"], name="email_type_idx")]

    @property
    def short_id(self):
        return self.subject

    def __str__(self):
        return "{} : {}".format(self.subject, self.receiver)


class FailedEmailAttempt(Exception):
    def __str__(self):
        return "Attempt to Send Email failed!"
