import datetime

from crispy_forms.bootstrap import PrependedAppendedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder, Layout, Submit
from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator

from ..models.instrument import Instrument
from ..models.slot import SlotManager
from ..models.user import CustomUser, Faculty, Student
from .fields import CrispyTimeField, DateInput, MinuteDurationField

EMAIL_CHOICES = (
    ("Yes", "Yes"),
    ("No", "No"),
)

BOOL_CHOICES = (
    (True, "Yes"),
    (False, "No"),
)

START_TIME_CHOICES = (
    ("00:00:00", "12 AM (Midnight)"),
    ("01:00:00", "01 AM"),
    ("02:00:00", "02 AM"),
    ("03:00:00", "03 AM"),
    ("04:00:00", "04 AM"),
    ("05:00:00", "05 AM"),
    ("06:00:00", "06 AM"),
    ("07:00:00", "07 AM"),
    ("08:00:00", "08 AM"),
    ("09:00:00", "09 AM"),
    ("10:00:00", "10 AM"),
    ("11:00:00", "11 AM"),
    ("12:00:00", "12 PM (Noon)"),
    ("13:00:00", "01 PM"),
    ("14:00:00", "02 PM"),
    ("15:00:00", "03 PM"),
    ("16:00:00", "04 PM"),
    ("17:00:00", "05 PM"),
    ("18:00:00", "06 PM"),
    ("19:00:00", "07 PM"),
    ("20:00:00", "08 PM"),
    ("21:00:00", "09 PM"),
    ("22:00:00", "10 PM"),
    ("23:00:00", "11 PM"),
)

DURATION = (
    ("1-hour", "1-hour"),
    ("2-hour", "2-hour"),
    ("3-hour", "3-hour"),
    ("4-hour", "4-hour"),
    ("6-hour", "6-hour"),
    ("8-hour", "8-hour"),
)

DELTA_DAYS = (
    ("1", "1-day (Selected Date only)"),
    ("7", "1-week"),
    ("14", "2-weeks"),
    ("30", "1-month"),
    ("60", "2-month"),
)


class BulkImportForm(forms.Form):
    """Form for importing users from CSV"""

    csv_file = forms.FileField(
        label="Uplaod CSV File", help_text="<a href=sample/>Download a sample CSV</a>"
    )
    send_email = forms.BooleanField(label="Send password details to users?")
    ignore_existing = forms.BooleanField(initial=True, label="Ignore if user exists?")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_class = "form-horizontal"
        self.helper.label_class = "col-sm-2"
        self.helper.field_class = "col-sm-3"
        self.helper.layout = Layout(
            "csv_file",
            "send_email",
            "ignore_existing",
            ButtonHolder(
                Submit("import_users", value="Import Users"),
            ),
        )


class BulkCreateSlotsForm(forms.Form):
    """Form for bulk time slot creation"""

    instrument = forms.ModelChoiceField(
        queryset=Instrument.objects.all(),
        label="Select Instrument",
    )
    start_date = forms.DateField(
        initial=datetime.date.today,
        widget=DateInput,
        label="Date from/on which the slot has to be made",
    )
    for_the_next = forms.ChoiceField(
        choices=DELTA_DAYS,
        label="For how many days do you want to add the slots?",
    )
    start_time = forms.TimeField(
        label="Start Time",
    )
    end_time = forms.TimeField(
        label="End Time",
    )
    slot_duration = MinuteDurationField(
        label="Slot Duration",
        help_text="The duration of each slot specified in minutes. If a whole number"
        " of slots cannot be created between the start and end time, no"
        " slots will be created.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_class = "form-horizontal"
        self.helper.label_class = "col-sm-2"
        self.helper.field_class = "col-sm-3"
        self.helper.layout = Layout(
            "instrument",
            "start_date",
            "for_the_next",
            CrispyTimeField("start_time"),
            CrispyTimeField("end_time"),
            PrependedAppendedText("slot_duration", appended_text="minutes"),
            ButtonHolder(Submit("add_slots", value="Add Slots")),
        )

    def clean(self):
        cleaned_data = super().clean()
        start_date: datetime.date = cleaned_data.get("start_date")
        start_time: datetime.time = cleaned_data.get("start_time")
        end_time: datetime.time = cleaned_data.get("end_time")
        duration: datetime.timedelta = cleaned_data.get("slot_duration")
        day_count = int(cleaned_data.get("for_the_next"))

        if start_time >= end_time:
            self.add_error(
                "start_time", ValidationError("Start time cannot be after end time.")
            )

        if start_date < datetime.date.today():
            self.add_error(
                "start_date", ValidationError("Start date cannot be before today.")
            )

        combined_start_time = datetime.datetime.combine(start_date, start_time)
        combined_end_time = datetime.datetime.combine(start_date, end_time)
        if duration and not float.is_integer(
            (combined_end_time - combined_start_time) / duration
        ):
            self.add_error(
                None,
                ValidationError(
                    "Cannot create whole number of slots between "
                    "specified start and end time with the given duration."
                ),
            )

        next_days = SlotManager.get_valid_slot_days(start_date, day_count)
        if not next_days:
            self.add_error(
                None,
                ValidationError(
                    "No days available to create slots! Note that "
                    "slots cannot be created on Sundays."
                ),
            )

        return cleaned_data


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("email", "name")


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ("email", "name")


class StudentCreationForm(CustomUserCreationForm):
    class Meta:
        model = Student
        fields = ("supervisor",)


class StudentChangeForm(CustomUserChangeForm):
    class Meta:
        model = Student
        fields = ("supervisor",)


class FacultyCreationForm(CustomUserCreationForm):
    class Meta:
        model = Faculty
        fields = ("department",)


class FacultyChangeForm(CustomUserChangeForm):
    class Meta:
        model = Faculty
        fields = ("department",)


class InstrumentCreateForm(forms.ModelForm):
    class Meta:
        model = Instrument
        fields = ("name", "desc", "status")
        widgets = {
            "status": forms.Select(choices=BOOL_CHOICES),
        }


class InstrumentChangeForm(forms.ModelForm):
    class Meta:
        model = Instrument
        fields = ("name", "desc", "status")
        widgets = {
            "status": forms.Select(choices=BOOL_CHOICES),
        }


class UtilisationReportForm(forms.Form):
    start_date = forms.DateField(
        initial=datetime.date(2024, 8, 1),
        widget=DateInput,
        label="Start date for usage report",
    )
    end_date = forms.DateField(
        initial=datetime.date.today, widget=DateInput, label="End date for usage report"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_class = "form-horizontal"
        self.helper.label_class = "col-sm-2"
        self.helper.field_class = "col-sm-3"
        self.helper.layout = Layout(
            "start_date",
            "end_date",
            ButtonHolder(Submit("download_report", value="Download Report")),
        )

    def clean(self):
        cleaned_data = super().clean()
        start_date: datetime.date = cleaned_data.get("start_date")
        end_date: datetime.date = cleaned_data.get("end_date")

        if start_date > end_date:
            self.add_error(
                "start_date", ValidationError("Start date cannot be after end date")
            )

        return cleaned_data


class TopUpForm(forms.Form):
    top_up_amount = forms.IntegerField(
        label="Top Up Amount", validators=[MinValueValidator(0)]
    )
