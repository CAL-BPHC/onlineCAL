from django.apps import AppConfig


class BookingPortalConfig(AppConfig):
    name = "booking_portal"

    def ready(self):
        self.create_django_q_scheduled_tasks()

    @staticmethod
    def create_django_q_scheduled_tasks():
        from datetime import datetime

        from django.db import IntegrityError, OperationalError, ProgrammingError
        from django_q.tasks import Schedule, schedule

        _date = datetime.now()
        date = datetime(_date.year, _date.month, _date.day)

        tasks = [
            {
                "args": "sendemails",
                "name": "Send Pending Emails",
                "schedule_type": Schedule.MINUTES,
                "minutes": 1,
                "next_run": date,
                "repeats": -1,
            },
            {
                "args": "cleanup_empty_slots",
                "name": "Cleanup past empty slots",
                "schedule_type": Schedule.DAILY,
                "next_run": date,
                "repeats": -1,
            },
            {
                "args": "cleanup_emails",
                "name": "Cleanup old email objects",
                "schedule_type": Schedule.DAILY,
                "next_run": date,
                "repeats": -1,
            },
        ]

        for task in tasks:
            try:
                schedule(
                    "django.core.management.call_command",
                    task["args"],
                    name=task["name"],  # Must be unique
                    schedule_type=task["schedule_type"],
                    minutes=task.get("minutes"),
                    next_run=task["next_run"],
                    repeats=task["repeats"],
                )
            except (ProgrammingError, IntegrityError, OperationalError):
                pass
