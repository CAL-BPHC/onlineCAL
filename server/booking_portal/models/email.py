from django.db import models


class EmailModel(models.Model):
    receiver = models.EmailField(null=True, blank=False)
    date_time = models.DateTimeField(auto_now_add=True)
    text = models.TextField()
    text_html = models.TextField()
    subject = models.CharField(max_length=100, null=True)
    sent = models.BooleanField()

    class Meta:
        verbose_name = "Email"
        verbose_name_plural = "Emails"
        default_related_name = "Emails"

    @property
    def short_id(self):
        return self.subject

    def __str__(self):
        return "{} : {}".format(self.subject, self.receiver)


class FailedEmailAttempt(Exception):
    def __str__(self):
        return "Attempt to Send Email failed!"
