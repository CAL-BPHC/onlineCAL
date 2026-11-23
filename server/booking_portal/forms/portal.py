from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder, Layout, Submit
from django import forms
from django.urls import reverse
from django.utils.timezone import localdate

from ..models.instrument import Instrument
from ..models.slot import Slot
from ..models.user import Student


class SlotModelChoiceField(forms.ModelChoiceField):
    """Provides customized representation for
    Slot Field in ModelChoiceField"""

    def label_from_instance(self, obj):
        # Returns description property of Slot Model
        return obj.description


class InstrumentList(forms.Form):
    """Form for selecting instruments for booking"""

    instruments = forms.ModelChoiceField(queryset=Instrument.objects.all())

    def __init__(self, *args, student=None, **kwargs):
        super().__init__(*args, **kwargs)
        if student is not None:
            self.fields["instruments"].queryset = student.instruments.all()

        self.helper = FormHelper(self)
        self.helper.form_show_labels = False
        self.helper.form_action = reverse("slot-list")
        self.helper.layout = Layout(
            "instruments",
            ButtonHolder(
                Submit("proceed", value="Proceed", css_class="btn-primary btn-md")
            ),
        )


class StudentSearchForm(forms.Form):
    """Narrows the students on the portal admin's instrument access page"""

    q = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Names, emails or instruments, separated by commas",
            }
        ),
    )

    def clean_q(self):
        # several at once, so a group trained together can be ticked together
        terms = (term.strip() for term in self.cleaned_data["q"].split(","))
        return [term for term in terms if term]


class InstrumentAccessForm(forms.Form):
    """Assigns one instrument to a student, or revokes it"""

    ASSIGN = "assign"
    REVOKE = "revoke"

    instrument = forms.ModelChoiceField(queryset=Instrument.objects.all())
    action = forms.ChoiceField(choices=((ASSIGN, "Assign"), (REVOKE, "Revoke")))


class BulkInstrumentAccessForm(InstrumentAccessForm):
    """Assigns one instrument to several students at once, or revokes it"""

    students = forms.ModelMultipleChoiceField(queryset=Student.objects.all())


class SlotList(forms.Form):
    """Form for selecting an empty slot of a given
    instrument"""

    def __init__(self, instr, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["slots"] = SlotModelChoiceField(
            queryset=Slot.objects.filter(
                instrument=instr, status=Slot.STATUS_1, date__gte=localdate()
            )
        )

        self.helper = FormHelper(self)
        self.helper.form_show_labels = False
        self.helper.form_action = reverse("book-machine", kwargs={"instr_id": instr.pk})
        self.helper.form_method = "GET"
        self.helper.layout = Layout(
            "slots",
            ButtonHolder(
                Submit("proceed", value="Proceed", css_class="btn-primary btn-md")
            ),
        )
