from django.core.mail import EmailMultiAlternatives, get_connection

# Gmail accepts at most 100 recipients (To + Cc + Bcc combined) on a message
# sent over SMTP: https://knowledge.workspace.google.com/admin/gmail/gmail-sending-limits-in-google-workspace
MAX_RECIPIENTS_PER_EMAIL = 100

# "To" header used on BCC-only emails so they don't go out with an empty header.
UNDISCLOSED_RECIPIENTS = "undisclosed-recipients:;"


def send_mass_html_mail(
    datatuple, fail_silently=False, user=None, password=None, connection=None
):
    """
    Given a datatuple of (subject, text_content, html_content, from_email,
    recipient_list, bcc_list), sends each message to each recipient list.
    Returns the number of emails sent.

    A message with an empty recipient_list is sent to the bcc_list only, with
    an "undisclosed-recipients" To header.

    If from_email is None, the DEFAULT_FROM_EMAIL setting is used.
    If auth_user and auth_password are set, they're used to log in.
    If auth_user is None, the EMAIL_HOST_USER setting is used.
    If auth_password is None, the EMAIL_HOST_PASSWORD setting is used.

    Source: https://stackoverflow.com/questions/7583801/send-mass-emails-with-emailmultialternatives/10215091#10215091
    """
    connection = connection or get_connection(
        username=user, password=password, fail_silently=fail_silently
    )
    messages = []
    for subject, text, html, from_email, recipient, bcc in datatuple:
        headers = {} if recipient else {"To": UNDISCLOSED_RECIPIENTS}
        message = EmailMultiAlternatives(
            subject, text, from_email, recipient, bcc=bcc, headers=headers
        )
        message.attach_alternative(html, "text/html")
        messages.append(message)
    return connection.send_messages(messages)
