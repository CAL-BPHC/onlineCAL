from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy


from .email import EmailModel
from .manager import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(gettext_lazy("email address"), unique=True, max_length=50)
    name = models.CharField(max_length=100)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    class Role(models.TextChoices):
        STAFF = "STAFF", "Staff"
        STUDENT = "STUDENT", "Student"
        FACULTY = "FACULTY", "Faculty"
        LAB_ASSISTANT = "LAB_ASSISTANT", "Lab Assistant"
        DEPARTMENT = "DEPARTMENT", "Department"

    role = models.CharField(max_length=50, choices=Role.choices)
    default_role = Role.STAFF

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    objects: CustomUserManager = CustomUserManager()

    def has_perm(self, perm, obj=None):
        if self.is_superuser:
            return True
        if self.is_staff and (
            "student" in perm
            or "faculty" in perm
            or "labassistant" in perm
            or "slot" in perm
            or "instrument" in perm
            or "announcement" in perm
        ):
            # Models accessible by lab assistants
            # TODO: Find a better way to add these permissions
            return True

        return False

    def has_module_perms(self, app_label):
        return self.is_staff

    def _create_email_obj(self, subject, message, html_message):
        EmailModel(
            receiver=self.email,
            text=message,
            text_html=html_message,
            subject=subject,
            sent=False,
        ).save()

    def send_email(self, subject, message, html_message):
        self._create_email_obj(subject, message, html_message)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.role = self.default_role
        return super().save(*args, **kwargs)

    @property
    def username(self):
        return self.email

    def __str__(self):
        return "{} ({})".format(self.name, self.email[: self.email.find("@")].lower())


class Department(CustomUser):
    default_role = CustomUser.Role.DEPARTMENT
    balance = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Department"
        default_related_name = "departments"


class Faculty(CustomUser):
    default_role = CustomUser.Role.FACULTY
    department = models.ForeignKey(Department, on_delete=models.PROTECT, null=True)
    balance = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Faculty"
        verbose_name_plural = "Faculties"
        default_related_name = "faculties"


class Student(CustomUser):
    default_role = CustomUser.Role.STUDENT
    supervisor = models.ForeignKey(Faculty, on_delete=models.PROTECT, null=False)

    class Meta:
        verbose_name = "Student"
        default_related_name = "students"


class LabAssistant(CustomUser):
    default_role = CustomUser.Role.LAB_ASSISTANT

    class Meta:
        verbose_name = "Lab Assistant"
        default_related_name = "labassistants"


class BalanceTopUpLog(models.Model):
    admin_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="admin_user"
    )
    top_up_amount = models.IntegerField(validators=[MinValueValidator(0)])
    date = models.DateTimeField(auto_now_add=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    recipient = GenericForeignKey("content_type", "object_id")

    def __str__(self):
        return (
            f"{self.admin_user} - {self.top_up_amount} - {self.date} - {self.recipient}"
        )
