from django.contrib import admin


class EmailAdmin(admin.ModelAdmin):
    list_display = ("receiver", "recipient_count", "email_type", "date_time", "sent")
    list_filter = ("sent", "email_type")
    search_fields = ("receiver", "bcc", "subject")

    def has_add_permission(self, request):
        # Emails are internally generated
        # Admins/staff cannot create and send an email object
        return False

    def has_change_permission(self, request, obj=None):
        # Once an email is sent, it cannot be changed by
        # admin/staff
        return False
