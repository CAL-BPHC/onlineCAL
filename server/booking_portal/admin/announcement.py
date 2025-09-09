from booking_portal.models import CustomUser
from booking_portal.models.email import EmailModel
from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import reverse


class AnnouncementAdmin(admin.ModelAdmin):
    def response_add(self, request, obj, post_url_continue=None):
        # We notify all users by email about the new announcement
        email_type = EmailModel.NEW_ANNOUNCEMENT
        context = {
            "recipient_name": "user",
            "announcement_title": obj.title,
            "announcement_url": "https://onlinecal.bits-hyderabad.ac.in"
            + reverse("announcements"),
        }
        text = render_to_string("email/new_announcement.txt", context)
        text_html = render_to_string("email/new_announcement.html", context)

        users = CustomUser.objects.filter(is_active=True)
        for user in users:
            if user.email.endswith("@email.com"):
                # Skip sending announcements to test users
                continue
            user.send_email(
                EmailModel.get_subject_for_type(email_type), text, text_html, email_type
            )

        return super().response_add(request, obj, post_url_continue)
