from crispy_forms.bootstrap import PrependedAppendedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder, Layout, Submit
from django.contrib.auth.forms import (AuthenticationForm, PasswordChangeForm,
                                       PasswordResetForm, SetPasswordForm)


class CustomLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['placeholder'] = 'Email ID'
        self.fields['password'].widget.attrs['placeholder'] = 'Password'

        self.helper = FormHelper(self)
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            PrependedAppendedText(
                'username',
                prepended_text='<i class="fas fa-envelope"></i>'
            ),
            PrependedAppendedText(
                'password',
                prepended_text='<i class="fas fa-key"></i>'
            ),
            ButtonHolder(
                Submit('login', value="Login", css_class='btn-lg btn-block')
            ),
        )


class CustomPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['email'].widget.attrs['placeholder'] = 'Email ID'

        self.helper = FormHelper(self)
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            PrependedAppendedText(
                'email',
                prepended_text='<i class="fas fa-envelope"></i>'
            ),
            ButtonHolder(
                Submit('submit', value="Reset Password",
                       css_class='btn-lg btn-block')
            ),
        )


class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['new_password1'].widget.attrs['placeholder'] = 'New Password'
        self.fields['new_password2'].widget.attrs['placeholder'] = 'Confirm Password'

        self.helper = FormHelper(self)
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            PrependedAppendedText(
                'new_password1',
                prepended_text='<i class="fas fa-key"></i>'
            ),
            PrependedAppendedText(
                'new_password2',
                prepended_text='<i class="fas fa-key"></i>'
            ),
            ButtonHolder(
                Submit('submit', value="Set New Password",
                       css_class='btn-lg btn-block')
            ),
        )


class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['old_password'].widget.attrs['placeholder'] = 'Old Password'
        self.fields['new_password1'].widget.attrs['placeholder'] = 'New Password'
        self.fields['new_password2'].widget.attrs['placeholder'] = 'Confirm Password'

        self.helper = FormHelper(self)
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            PrependedAppendedText(
                'old_password',
                prepended_text='<i class="fas fa-key"></i>'
            ),
            PrependedAppendedText(
                'new_password1',
                prepended_text='<i class="fas fa-key"></i>'
            ),
            PrependedAppendedText(
                'new_password2',
                prepended_text='<i class="fas fa-key"></i>'
            ),
            ButtonHolder(
                Submit('submit', value="Set New Password",
                       css_class='btn-lg btn-block')
            ),
        )
