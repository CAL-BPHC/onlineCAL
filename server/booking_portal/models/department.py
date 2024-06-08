from django.db import models
from django.utils.translation import gettext_lazy


class Department(models.Model):
    name = models.CharField(max_length=100)
    balance = models.IntegerField()
    hod_email = models.EmailField(gettext_lazy(
        "email address"), unique=True, max_length=100)
    hod_name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "Departments"
        default_related_name = "departments"
