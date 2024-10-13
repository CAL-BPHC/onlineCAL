import csv
from functools import update_wrapper
from io import BytesIO, StringIO, TextIOWrapper

from django.contrib import messages
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import validate_email
from django.db import transaction
from django.http import FileResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import path
from django.utils.html import escape
from django.utils.safestring import mark_safe

from ... import forms


class CustomUserAdmin(UserAdmin):
    """CustomUser Admin Portal.
    Student/Faculty/Lab Assistant inherit this admin
    class
    """

    CSV_HEADERS = ("name", "email", "password")

    form = forms.CustomUserChangeForm
    add_form = forms.CustomUserCreationForm

    list_display = ("name", "email", "role")
    list_filter = ("role",)
    fieldsets = (
        (
            None,
            {"fields": ("email", "name", "password")},
        ),
        ("Permissions", {"fields": ("is_staff", "is_active")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "name",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                    "role",
                ),
            },
        ),
    )

    search_fields = ("email",)
    ordering = ("email",)

    def get_urls(self):
        urls = super().get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        my_urls = [
            path("import-csv/", wrap(self.import_csv), name="%s_%s_import-csv" % info),
            path(
                "import-csv/sample/",
                wrap(self.import_csv_sample),
                name="%s_%s_import-csv-sample" % info,
            ),
        ]
        return my_urls + urls

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["bulk_add_text"] = "Import from CSV"
        extra_context["bulk_add_url"] = "import-csv/"
        return super().changelist_view(request, extra_context)

    @transaction.atomic
    def create_users(
        self, user_type, records, staff=False, notify_user=False, skip_existing=True
    ):
        """
        Function to create users in bulk from a set of records
        """
        headers = self.get_csv_headers()
        if set(records.fieldnames) != set(headers):
            raise Exception(f"Invalid CSV headers/columns. Expected: {headers}")

        created_users = []
        for record in records:
            record["email"] = record["email"].strip()
            record["name"] = record["name"].strip()

            if not record["password"]:
                record["password"] = user_type.objects.make_random_password(8)
            raw_password = record["password"]
            record["password"] = make_password(raw_password)

            if user_type.objects.filter(email=record["email"]).exists():
                if not skip_existing:
                    raise ObjectDoesNotExist(
                        f"User with username \"{record['email']}\" already exists."
                    )
                else:
                    continue

            record = self._validate_record(record)
            user = user_type.objects.create(**record, is_staff=staff)

            if notify_user:
                text = render_to_string(
                    "email/welcome.txt",
                    {
                        "recipient_name": user.name,
                        "email": user.email,
                        "password": raw_password,
                        "user_type": user_type.__name__,
                    },
                )
                text_html = render_to_string(
                    "email/welcome.html",
                    {
                        "recipient_name": user.name,
                        "email": user.email,
                        "password": raw_password,
                        "user_type": user_type.__name__,
                    },
                )

                user.send_email(
                    subject="Welcome to OnlineCAL!",
                    message=text,
                    html_message=text_html,
                )

                created_users.append(user.name)
        return created_users

    def import_csv(self, request):
        """
        Function to bulk import user details from a CSV file
        """
        if request.method == "POST":
            form = forms.BulkImportForm(request.POST, request.FILES)
            if not form.is_valid():
                self.message_user(request, "Error: Invalid form", level=messages.ERROR)
                return self.render_bulk_import_form(request, form)

            try:
                csv_file = TextIOWrapper(
                    form.cleaned_data["csv_file"], encoding=request.encoding
                )
                dialect = csv.Sniffer().sniff(csv_file.read())
                csv_file.seek(0)
                reader = csv.DictReader(csv_file, dialect=dialect)
            except Exception as err:
                self.message_user(
                    request, "Error: {}".format(err), level=messages.ERROR
                )
                return self.render_bulk_import_form(request, form)

            try:
                send_email = form.cleaned_data["send_email"]
                ignore_existing = form.cleaned_data["ignore_existing"]

                user_type = self.get_user_type(request)
                staff = self.is_user_staff()

                created_users = self.create_users(
                    user_type, reader, staff, send_email, skip_existing=ignore_existing
                )
            except Exception as err:
                self.message_user(
                    request,
                    f"Error on row number {reader.line_num}: {err}",
                    level=messages.ERROR,
                )
                return self.render_bulk_import_form(request, form)
            else:
                created_users = [escape(x) for x in created_users]
                names = "<br/>".join(created_users)
                self.message_user(
                    request,
                    mark_safe(
                        "{} users have been created:<br/>{}".format(
                            len(created_users), names
                        )
                    ),
                )
                return redirect("..")

        else:
            return self.render_bulk_import_form(request, forms.BulkImportForm())

    def render_bulk_import_form(self, request, form):
        payload = {
            "form": form,
            "opts": self.get_user_type(request)._meta,
            "has_view_permission": True,
        }
        return render(request, "admin/bulk_import_form.html", payload)

    def import_csv_sample(self, request):
        sio = StringIO()
        writer = csv.DictWriter(sio, fieldnames=self.get_csv_headers())
        writer.writeheader()

        bio = BytesIO(sio.getvalue().encode("utf-8"))
        user_type = self.get_user_type(request).__name__.lower()
        return FileResponse(bio, as_attachment=True, filename=f"import_{user_type}.csv")

    def get_user_type(self, request):
        raise NotImplementedError(
            "Derived classes should return a Model for the user type"
        )

    def is_user_staff(self):
        raise NotImplementedError("Derived classes should return a boolean")

    def _validate_record(self, record):
        if not record["name"] or not record["email"]:
            raise ValidationError("Email or name not found")

        # This call will raise validation error
        validate_email(record["email"])
        return record

    def get_csv_headers(self):
        return self.CSV_HEADERS
