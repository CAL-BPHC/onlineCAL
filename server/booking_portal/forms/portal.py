from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Submit
from django import forms
from django.urls import reverse
from django.utils.timezone import now

from ..models.instrument import Instrument
from ..models.slot import Slot


class SlotModelChoiceField(forms.ModelChoiceField):
    """Provides customized representation for
    Slot Field in ModelChoiceField"""

    def label_from_instance(self, obj):
        # Returns description property of Slot Model
        return obj.description


class InstrumentList(forms.Form):
    """Form for selecting instruments for booking"""
    instruments = forms.ModelChoiceField(queryset=Instrument.objects.all())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)

        self.helper = FormHelper(self)
        self.helper.form_show_labels = False
        self.helper.form_action = reverse('slot-list')
        self.helper.layout = Layout(
            'instruments',
            ButtonHolder(
                Submit('proceed', value="Proceed",
                       css_class='btn-primary btn-md')
            )
        )


class SlotList(forms.Form):
    """Form for selecting an empty slot of a given
    instrument"""

    def __init__(self, instr, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slots'] = SlotModelChoiceField(
            queryset=Slot.objects.filter(
                instrument=instr,
                status=Slot.STATUS_1,
                date__gte=now().date()
            )
        )

        self.helper = FormHelper(self)
        self.helper.form_show_labels = False
        self.helper.form_action = reverse(
            'book-machine', kwargs={'instr_id': instr.pk})
        self.helper.form_method = 'GET'
        self.helper.layout = Layout(
            'slots',
            ButtonHolder(
                Submit('proceed', value="Proceed",
                       css_class='btn-primary btn-md')
            )
        )
