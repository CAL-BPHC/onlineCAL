import datetime

from crispy_forms.layout import Field as CrispyField
from django import forms
from django.core.exceptions import ValidationError


class DateInput(forms.DateInput):
    input_type = "date"


class CrispyTimeField(CrispyField):
    def __init__(self, *args, **kwargs):
        kwargs["template"] = "widgets/time_input.html"
        kwargs["css_class"] = "datetimepicker-input"
        super().__init__(*args, **kwargs)


class MinuteDurationField(forms.DurationField):
    default_error_messages = {
        "invalid": "The duration in minutes must be a positive integer."
    }

    def to_python(self, value):
        validation_error = ValidationError(self.error_messages["invalid"])
        if isinstance(value, datetime.timedelta):
            return value

        try:
            value = int(value)
        except (ValueError, TypeError):
            raise validation_error
        else:
            if value > 0:
                return datetime.timedelta(minutes=int(value))
            raise validation_error
