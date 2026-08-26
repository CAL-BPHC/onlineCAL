import datetime

from django.core.paginator import Paginator
from django.http import QueryDict
from django.test import Client, TestCase

from ..factories import InstrumentFactory, StudentFactory
from ..models import Department, Slot, StudentRequest
from ..models.faculty_request import FacultyRequest
from ..models.instrument.requests import FTIR
from ..views.user.portal import BasePortalFilter, get_pagintion_nav_range

ALL_STATUSES = [status for status, _ in StudentRequest.STATUS_CHOICES]


class RequestBuilderMixin:
    """Builds student requests with a real form object so cost works."""

    def build_portal_fixtures(self, instrument_name="FTIR"):
        self.student = StudentFactory()
        self.faculty = self.student.supervisor
        # Requests routed to a department email it on save, so the supervisor
        # needs one exactly like they do in the portal.
        self.department = Department.objects.create(
            email="department@example.com", name="chemistry"
        )
        self.faculty.department = self.department
        self.faculty.save()
        self.instrument = InstrumentFactory(name=instrument_name)

    def make_form(self, number_of_samples=1):
        return FTIR.objects.create(
            phone_number="1234567890",
            date=datetime.date(2025, 6, 1),
            time=datetime.time(9),
            duration="2 hours",
            number_of_samples=number_of_samples,
            sample_from_outside="No",
            origin_of_sample="lab",
            req_discussed="Yes",
            sample_code="X",
            composition="Y",
            state="Solid",
            solvent="Z",
        )

    def make_slot(self, date, hours=2, instrument=None):
        return Slot.objects.create(
            instrument=instrument or self.instrument,
            date=date,
            start_time=datetime.time(9),
            end_time=datetime.time(9 + hours),
            status=Slot.STATUS_3,
        )

    def make_request(
        self, status, date=datetime.date(2025, 6, 1), hours=2, cost=100, **kwargs
    ):
        return StudentRequest.objects.create(
            student=kwargs.pop("student", self.student),
            faculty=kwargs.pop("faculty", self.faculty),
            instrument=kwargs.pop("instrument", self.instrument),
            slot=self.make_slot(date, hours, kwargs.pop("slot_instrument", None)),
            status=status,
            mode_description="flat",
            mode_cost=cost,
            mode_rule_type="FLAT",
            content_object=self.make_form(),
            **kwargs,
        )


class PortalFilterTestCase(RequestBuilderMixin, TestCase):
    def setUp(self):
        self.build_portal_fixtures()

    def filtered(self, params):
        return BasePortalFilter(
            QueryDict(params),
            queryset=StudentRequest.objects.filter(faculty=self.faculty),
        ).qs

    def test_status_filter_returns_only_the_selected_status(self):
        for offset, status in enumerate(ALL_STATUSES):
            self.make_request(status, datetime.date(2025, 6, 1 + offset))

        for status in ALL_STATUSES:
            with self.subTest(status=status):
                self.assertEqual(
                    [request.status for request in self.filtered(f"status={status}")],
                    [status],
                )

    def test_status_filter_offers_every_status(self):
        form = BasePortalFilter(
            QueryDict(""), queryset=StudentRequest.objects.all()
        ).form
        choices = dict(form.fields["status"].choices)
        for status in ALL_STATUSES:
            self.assertIn(status, choices)

    def test_date_filters_include_both_boundary_dates(self):
        dates = [
            datetime.date(2025, 4, 1),
            datetime.date(2025, 8, 15),
            datetime.date(2026, 3, 31),
        ]
        for date in dates:
            self.make_request(StudentRequest.APPROVED, date)

        found = self.filtered("from_date=2025-04-01&to_date=2026-03-31")
        self.assertEqual(sorted(request.slot.date for request in found), dates)

    def test_ordering_uses_the_slot_date_not_the_slot_id(self):
        # Insert the later date first so row order and date order disagree.
        self.make_request(StudentRequest.APPROVED, datetime.date(2025, 12, 1))
        self.make_request(StudentRequest.APPROVED, datetime.date(2025, 1, 1))

        ordered = self.filtered("order=slot__date")
        self.assertEqual(
            [request.slot.date for request in ordered],
            [datetime.date(2025, 1, 1), datetime.date(2025, 12, 1)],
        )

    def test_nav_range_includes_the_last_page(self):
        paginator = Paginator(list(range(60)), BasePortalFilter.PORTAL_PAGE_SIZE)
        self.assertEqual(list(get_pagintion_nav_range(paginator.page(1))), [1, 2, 3])

    def test_faculty_request_filter_drops_the_student_only_status(self):
        form = BasePortalFilter(
            QueryDict(""), queryset=FacultyRequest.objects.all()
        ).form
        choices = dict(form.fields["status"].choices)
        self.assertNotIn(StudentRequest.WAITING_FOR_FACULTY, choices)
        self.assertIn(FacultyRequest.APPROVED, choices)


class PortalPageTestCase(RequestBuilderMixin, TestCase):
    """The filter reaching the rendered page, not just the filterset."""

    def setUp(self):
        self.build_portal_fixtures(instrument_name="NMR")
        self.client = Client()
        self.client.force_login(self.faculty)

    def test_status_filter_applies_on_the_faculty_portal(self):
        for offset, status in enumerate(ALL_STATUSES):
            self.make_request(status, datetime.date(2025, 6, 1 + offset))

        response = self.client.get("/faculty/", {"status": StudentRequest.APPROVED})

        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        cell = '<td class="js-request-status">{}</td>'.format
        self.assertIn(cell("Approved"), body)
        self.assertNotIn(cell("Rejected"), body)
        self.assertNotIn(cell("Waiting for Faculty Approval"), body)

    def test_pagination_links_render(self):
        for offset in range(30):
            self.make_request(
                StudentRequest.APPROVED,
                datetime.date(2025, 6, 1) + datetime.timedelta(days=offset),
            )

        response = self.client.get("/faculty/")

        self.assertContains(response, 'href="?page=2"')
