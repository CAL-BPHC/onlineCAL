from crispy_forms.bootstrap import PrependedAppendedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder, Layout, Submit
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
)


class CustomLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].widget.attrs["placeholder"] = "Email ID"
        self.fields["password"].widget.attrs["placeholder"] = "Password"

        self.helper = FormHelper(self)
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            PrependedAppendedText(
                "username", prepended_text='<i class="fas fa-envelope"></i>'
            ),
            PrependedAppendedText(
                "password", prepended_text='<i class="fas fa-key"></i>'
            ),
            ButtonHolder(Submit("login", value="Login", css_class="btn-lg btn-block")),
        )


class CustomPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["email"].widget.attrs["placeholder"] = "Email ID"

        self.helper = FormHelper(self)
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            PrependedAppendedText(
                "email", prepended_text='<i class="fas fa-envelope"></i>'
            ),
            ButtonHolder(
                Submit("submit", value="Reset Password", css_class="btn-lg btn-block")
            ),
        )

    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None,
    ):
        """Inject recipient_name into the email context.

        Django's built-in PasswordResetForm passes a context containing
        'user'. The base email template expects 'recipient_name', so we
        add it here just before delegating to the parent implementation.
        """
        user = context.get("user")
        if user and getattr(user, "name", None):
            context["recipient_name"] = user.name
        else:
            context.setdefault("recipient_name", "User")
        super().send_mail(
            subject_template_name,
            email_template_name,
            context,
            from_email,
            to_email,
            html_email_template_name,
        )


class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["new_password1"].widget.attrs["placeholder"] = "New Password"
        self.fields["new_password2"].widget.attrs["placeholder"] = "Confirm Password"

        self.helper = FormHelper(self)
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            PrependedAppendedText(
                "new_password1", prepended_text='<i class="fas fa-key"></i>'
            ),
            PrependedAppendedText(
                "new_password2", prepended_text='<i class="fas fa-key"></i>'
            ),
            ButtonHolder(
                Submit("submit", value="Set New Password", css_class="btn-lg btn-block")
            ),
        )


class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["old_password"].widget.attrs["placeholder"] = "Old Password"
        self.fields["new_password1"].widget.attrs["placeholder"] = "New Password"
        self.fields["new_password2"].widget.attrs["placeholder"] = "Confirm Password"

        self.helper = FormHelper(self)
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            PrependedAppendedText(
                "old_password", prepended_text='<i class="fas fa-key"></i>'
            ),
            PrependedAppendedText(
                "new_password1", prepended_text='<i class="fas fa-key"></i>'
            ),
            PrependedAppendedText(
                "new_password2", prepended_text='<i class="fas fa-key"></i>'
            ),
            ButtonHolder(
                Submit("submit", value="Set New Password", css_class="btn-lg btn-block")
            ),
        )
