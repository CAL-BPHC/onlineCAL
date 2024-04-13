from django import forms

from booking_portal.models import UserDetail, UserRemark
from booking_portal.models import Faculty, Student


class MyModelChoiceField(forms.ModelChoiceField):

    def label_from_instance(self, obj):
        return "{} ({})".format(obj.name, obj.email)


class UserDetailsForm(forms.ModelForm):

    user_name = MyModelChoiceField(
        queryset=Student.objects.all(),
        label='Email Id',
        widget=forms.Select(
            attrs={
                'class': 'form-control',
            }
        ),
    )

    sup_name = MyModelChoiceField(
        queryset=Faculty.objects.all(),
        label='Supervisor Name',
        widget=forms.Select(
            attrs={
                'class': 'form-control',
            }
        )
    )

    def __init__(self, *args, **kwargs):
        super(UserDetailsForm, self).__init__(*args, **kwargs)
        self.fields['user_name'].widget.attrs['disabled'] = True
        self.fields['sup_name'].widget.attrs['disabled'] = True
        self.fields['time'].widget.attrs['disabled'] = True
        self.fields['date'].widget.attrs['disabled'] = True
        self.fields['duration'].widget.attrs['readonly'] = True
        self.fields['sup_dept'].widget.attrs['readonly'] = True

        is_student = (kwargs.get('initial').get('is_student'))
        if is_student:
            self.fields['user_name'].queryset = Student.objects.all()
        else:
            self.fields['user_name'].queryset = Faculty.objects.all()
            self.fields['sup_name'].required = False
            self.fields['sup_name'].widget = forms.HiddenInput()
            self.fields['sup_dept'].required = False
            self.fields['sup_dept'].widget = forms.HiddenInput()

    class Meta:
        model = UserDetail
        fields = (
            'user_name',
            'phone_number',
            'date',
            'time',
            'duration',
            'sup_name',
            'sup_dept',
            'number_of_samples',
            'sample_from_outside',
            'origin_of_sample',
            'req_discussed'
        )
        labels = {
            'duration': 'Slot Duration',
            'sup_dept': 'Supervisor Department',
            'sample_from_outside': 'Is the sample obtained from outside BITS through collaboration?',
            'origin_of_sample': 'Provide origin of sample',
            'req_discussed': 'Have the sampling modalities and requirements been discussed with the operator?',
        }
        widgets = {
            'phone_number': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),
            'date': forms.SelectDateWidget(
                attrs={
                    'class': 'form-control',
                }
            ),
            'time': forms.TimeInput(
                attrs={
                    'type': 'time',
                    'class': 'form-control',
                }
            ),
            'duration': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }
            ),
            'sup_dept': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }
            ),
            'number_of_samples': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                }
            ),
            'sample_from_outside': forms.Select(
                attrs={
                    'class': 'form-control',
                }
            ),
            'origin_of_sample': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }
            ),
            'req_discussed': forms.Select(
                attrs={
                    'class': 'form-control',
                }
            ),
        }


class UserRemarkForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['faculty_remarks'].widget.attrs['readonly'] = True
        self.fields['lab_assistant_remarks'].widget.attrs['readonly'] = True

    class Meta:
        model = UserRemark
        fields = (
            "student_remarks",
            "faculty_remarks",
            "lab_assistant_remarks",
        )

        labels = {
            "student_remarks": 'Any other relevant information',
            "faculty_remarks": "Supervisor's Remarks (if any)",
            "lab_assistant_remarks": "Lab Assistant's Remarks (if any)"
        }

        widgets = {
            "student_remarks": forms.Textarea(
                attrs={
                    'class': 'form-control',
                }
            ),

            "faculty_remarks": forms.Textarea(
                attrs={
                    'class': 'form-control',
                }
            ),

            "lab_assistant_remarks": forms.Textarea(
                attrs={
                    'class': 'form-control',
                }
            )
        }
