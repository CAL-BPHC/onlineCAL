import datetime

from django.test import Client, TestCase

from .. import reporting
from ..factories import FacultyFactory, InstrumentFactory, StudentFactory
from ..models import Slot, StudentRequest
from ..models.faculty_request import FacultyRequest
from .test_portal_filters import RequestBuilderMixin

USAGE_URL = "/faculty/usage-summary"


class FinancialYearTestCase(TestCase):
    def test_bounds_before_and_after_april(self):
        self.assertEqual(
            reporting.financial_year_bounds(datetime.date(2025, 6, 10)),
            (datetime.date(2025, 4, 1), datetime.date(2026, 3, 31)),
        )
        self.assertEqual(
            reporting.financial_year_bounds(datetime.date(2026, 1, 10)),
            (datetime.date(2025, 4, 1), datetime.date(2026, 3, 31)),
        )

    def test_first_and_last_day_belong_to_their_year(self):
        self.assertEqual(
            reporting.financial_year_bounds(datetime.date(2025, 4, 1))[0],
            datetime.date(2025, 4, 1),
        )
        self.assertEqual(
            reporting.financial_year_bounds(datetime.date(2026, 3, 31))[1],
            datetime.date(2026, 3, 31),
        )

    def test_label(self):
        self.assertEqual(
            reporting.financial_year_label(datetime.date(2025, 4, 1)), "FY 25-26"
        )

    def test_resolve_range_presets(self):
        today = datetime.date(2025, 9, 15)
        self.assertEqual(
            reporting.resolve_range("this_fy", today=today)[:2],
            (datetime.date(2025, 4, 1), datetime.date(2026, 3, 31)),
        )
        self.assertEqual(
            reporting.resolve_range("last_fy", today=today)[:2],
            (datetime.date(2024, 4, 1), datetime.date(2025, 3, 31)),
        )
        self.assertEqual(
            reporting.resolve_range("this_month", today=today)[:2],
            (datetime.date(2025, 9, 1), datetime.date(2025, 9, 30)),
        )
        self.assertEqual(
            reporting.resolve_range("last_3_months", today=today)[:2],
            (datetime.date(2025, 6, 15), today),
        )
        self.assertEqual(
            reporting.resolve_range("all_time", today=today)[:2], (None, None)
        )

    def test_backwards_custom_range_is_swapped(self):
        start, end, _ = reporting.resolve_range(
            "custom", datetime.date(2025, 5, 1), datetime.date(2025, 1, 1)
        )
        self.assertEqual(
            (start, end), (datetime.date(2025, 1, 1), datetime.date(2025, 5, 1))
        )


class UsageSummaryTestCase(RequestBuilderMixin, TestCase):
    def setUp(self):
        self.build_portal_fixtures()
        self.other_student = StudentFactory(supervisor=self.faculty)
        self.nmr = InstrumentFactory(name="NMR")
        self.client = Client()
        self.client.force_login(self.faculty)

    def summary(self, **params):
        params.setdefault("preset", "custom")
        params.setdefault("from", "2025-04-01")
        params.setdefault("to", "2026-03-31")
        return self.client.get(USAGE_URL, params).json()

    def test_only_approved_bookings_reach_the_totals(self):
        self.make_request(
            StudentRequest.APPROVED, datetime.date(2025, 5, 1), hours=2, cost=100
        )
        self.make_request(StudentRequest.WAITING_FOR_FACULTY, datetime.date(2025, 5, 2))
        self.make_request(StudentRequest.REJECTED, datetime.date(2025, 5, 3))

        totals = self.summary()["totals"]

        self.assertEqual(totals["bookings"], 1)
        self.assertEqual(totals["hours"], 2.0)
        self.assertEqual(totals["cost"], 100.0)

    def test_queue_tracks_the_approval_chain(self):
        self.make_request(StudentRequest.WAITING_FOR_FACULTY, datetime.date(2025, 5, 1))
        self.make_request(StudentRequest.WAITING_FOR_FACULTY, datetime.date(2025, 5, 2))
        self.make_request(
            StudentRequest.WAITING_FOR_DEPARTMENT, datetime.date(2025, 5, 3)
        )
        self.make_request(
            StudentRequest.WAITING_FOR_LAB_ASST, datetime.date(2025, 5, 4)
        )
        self.make_request(StudentRequest.APPROVED, datetime.date(2025, 5, 5))
        self.make_request(StudentRequest.REJECTED, datetime.date(2025, 5, 6))

        queue = self.summary()["queue"]

        self.assertEqual(queue["awaiting_you"]["bookings"], 2)
        # everything past this faculty's gate; rejected is not counted
        self.assertEqual(queue["cleared_by_you"]["bookings"], 3)
        self.assertEqual(queue["with_department"]["bookings"], 1)
        self.assertEqual(queue["with_lab"]["bookings"], 1)

    def test_queue_follows_the_selected_date_range(self):
        self.make_request(StudentRequest.WAITING_FOR_FACULTY, datetime.date(2019, 1, 7))
        self.make_request(StudentRequest.WAITING_FOR_FACULTY, datetime.date(2025, 5, 7))

        payload = self.summary()  # range is 2025-04-01 to 2026-03-31

        self.assertEqual(payload["queue"]["awaiting_you"]["bookings"], 1)
        self.assertEqual(
            self.summary(preset="all_time")["queue"]["awaiting_you"]["bookings"], 2
        )

    def test_queue_follows_the_instrument_but_not_the_status(self):
        self.make_request(StudentRequest.WAITING_FOR_FACULTY, datetime.date(2025, 5, 1))
        self.make_request(
            StudentRequest.WAITING_FOR_FACULTY,
            datetime.date(2025, 5, 2),
            instrument=self.nmr,
            slot_instrument=self.nmr,
        )

        payload = self.summary(instrument=self.nmr.pk, status=StudentRequest.APPROVED)

        # narrowed by instrument, but a status filter must not empty the queue
        # of the very statuses it exists to report
        self.assertEqual(payload["queue"]["awaiting_you"]["bookings"], 1)
        self.assertEqual(payload["totals"]["bookings"], 0)

    def test_queue_counts_hours_and_cost_on_each_side(self):
        self.make_request(StudentRequest.WAITING_FOR_DEPARTMENT, hours=3, cost=300)
        self.make_request(StudentRequest.WAITING_FOR_FACULTY, hours=2, cost=150)

        queue = self.summary()["queue"]

        self.assertEqual(queue["cleared_by_you"]["hours"], 3.0)
        self.assertEqual(queue["cleared_by_you"]["cost"], 300.0)
        self.assertEqual(queue["awaiting_you"]["hours"], 2.0)
        self.assertEqual(queue["awaiting_you"]["cost"], 150.0)

    def test_breakdowns_cover_students_and_own_bookings(self):
        self.make_request(
            StudentRequest.APPROVED, datetime.date(2025, 5, 1), hours=2, cost=100
        )
        self.make_request(
            StudentRequest.APPROVED,
            datetime.date(2025, 5, 2),
            hours=1,
            cost=50,
            student=self.other_student,
        )
        FacultyRequest.objects.create(
            faculty=self.faculty,
            instrument=self.nmr,
            slot=self.make_slot(
                datetime.date(2025, 5, 3), hours=4, instrument=self.nmr
            ),
            status=FacultyRequest.APPROVED,
            mode_description="flat",
            mode_cost=400,
            mode_rule_type="FLAT",
            content_object=self.make_form(),
        )

        payload = self.summary()

        self.assertEqual(payload["totals"]["hours"], 7.0)
        self.assertEqual(payload["totals"]["cost"], 550.0)

        by_instrument = {row["key"]: row for row in payload["by_instrument"]}
        self.assertEqual(by_instrument["NMR"]["hours"], 4.0)
        self.assertEqual(by_instrument["FTIR"]["hours"], 3.0)
        self.assertEqual(
            {child["key"] for child in by_instrument["NMR"]["children"]},
            {reporting.usage.OWN_BOOKING_LABEL},
        )

        by_student = {row["key"]: row for row in payload["by_student"]}
        self.assertIn(reporting.usage.OWN_BOOKING_LABEL, by_student)
        self.assertEqual(by_student[str(self.student)]["hours"], 2.0)

    def test_a_broken_form_object_does_not_break_the_panel(self):
        request = self.make_request(
            StudentRequest.APPROVED, datetime.date(2025, 5, 1), hours=2, cost=100
        )
        request.object_id = 10**6
        request.save(update_fields=["object_id"])

        totals = self.summary()["totals"]

        self.assertEqual(totals["bookings"], 1)
        self.assertEqual(totals["hours"], 2.0)
        self.assertEqual(totals["cost"], 0.0)

    def test_another_faculty_usage_never_leaks(self):
        stranger = FacultyFactory()
        self.make_request(
            StudentRequest.APPROVED,
            datetime.date(2025, 5, 1),
            hours=3,
            cost=999,
            faculty=stranger,
        )

        self.assertEqual(self.summary()["totals"]["bookings"], 0)

    def test_range_is_respected(self):
        self.make_request(StudentRequest.APPROVED, datetime.date(2025, 4, 1))
        self.make_request(StudentRequest.APPROVED, datetime.date(2026, 3, 31))
        self.make_request(StudentRequest.APPROVED, datetime.date(2026, 4, 1))

        self.assertEqual(self.summary()["totals"]["bookings"], 2)

    def test_instrument_scopes_the_totals(self):
        self.make_request(
            StudentRequest.APPROVED, datetime.date(2025, 5, 1), hours=2, cost=100
        )
        self.make_request(
            StudentRequest.APPROVED,
            datetime.date(2025, 5, 2),
            hours=4,
            cost=200,
            instrument=self.nmr,
            slot_instrument=self.nmr,
        )

        payload = self.summary(instrument=self.nmr.pk)

        self.assertEqual(payload["totals"]["bookings"], 1)
        self.assertEqual(payload["totals"]["hours"], 4.0)
        self.assertEqual(payload["range"]["instrument"], "NMR")
        self.assertEqual([row["key"] for row in payload["by_instrument"]], ["NMR"])

    def test_status_scopes_the_totals(self):
        self.make_request(
            StudentRequest.APPROVED, datetime.date(2025, 5, 1), hours=2, cost=100
        )
        self.make_request(
            StudentRequest.WAITING_FOR_DEPARTMENT,
            datetime.date(2025, 5, 2),
            hours=5,
            cost=300,
        )

        payload = self.summary(status=StudentRequest.WAITING_FOR_DEPARTMENT)

        self.assertEqual(payload["totals"]["bookings"], 1)
        self.assertEqual(payload["totals"]["hours"], 5.0)
        self.assertEqual(payload["basis"]["label"], "Waiting for department approval")
        self.assertTrue(payload["basis"]["counts_towards_usage"])

    def test_rejected_and_cancelled_never_add_to_usage(self):
        self.make_request(
            StudentRequest.REJECTED, datetime.date(2025, 5, 1), hours=9, cost=900
        )
        self.make_request(
            StudentRequest.CANCELLED, datetime.date(2025, 5, 2), hours=7, cost=700
        )

        for status in (StudentRequest.REJECTED, StudentRequest.CANCELLED):
            with self.subTest(status=status):
                payload = self.summary(status=status)
                self.assertEqual(payload["totals"]["hours"], 0)
                self.assertEqual(payload["totals"]["cost"], 0)
                self.assertEqual(payload["totals"]["bookings"], 0)
                self.assertEqual(payload["by_instrument"], [])
                self.assertFalse(payload["basis"]["counts_towards_usage"])

    def test_unknown_instrument_or_status_is_rejected(self):
        self.assertEqual(
            self.client.get(USAGE_URL, {"instrument": 99999}).status_code, 400
        )
        self.assertEqual(self.client.get(USAGE_URL, {"status": "R9"}).status_code, 400)

    def test_unknown_preset_is_rejected(self):
        self.assertEqual(
            self.client.get(USAGE_URL, {"preset": "nope"}).status_code, 400
        )

    def test_custom_range_needs_a_date(self):
        self.assertEqual(
            self.client.get(USAGE_URL, {"preset": "custom"}).status_code, 400
        )

    def test_students_cannot_read_faculty_usage(self):
        client = Client()
        client.force_login(self.student)
        self.assertEqual(client.get(USAGE_URL).status_code, 302)


class RequestActionTestCase(RequestBuilderMixin, TestCase):
    def setUp(self):
        self.build_portal_fixtures()
        self.client = Client()
        self.client.force_login(self.faculty)

    def test_accepting_routes_the_request_onward(self):
        request = self.make_request(StudentRequest.WAITING_FOR_FACULTY)

        response = self.client.post(
            f"/requests_faculty/accept/{request.id}", {"departmentRoute": "True"}
        )

        self.assertEqual(response.status_code, 302)
        request.refresh_from_db()
        self.assertEqual(request.status, StudentRequest.WAITING_FOR_DEPARTMENT)

    def test_rejecting_marks_the_request_rejected(self):
        request = self.make_request(StudentRequest.WAITING_FOR_FACULTY)

        response = self.client.post(f"/requests_faculty/reject/{request.id}")

        self.assertEqual(response.status_code, 302)
        request.refresh_from_db()
        self.assertEqual(request.status, StudentRequest.REJECTED)

    def test_a_post_survives_the_tls_terminating_proxy(self):
        """A decision as it arrives in production.

        nginx terminates TLS, so Django has to read the forwarded scheme or it
        rebuilds an http:// origin and rejects any POST that carries an Origin
        header as a bad origin.
        """
        request = self.make_request(StudentRequest.WAITING_FOR_FACULTY)
        host = "portal.example.com"
        client = Client(enforce_csrf_checks=True, HTTP_HOST=host)
        client.force_login(self.faculty)
        client.get("/auth/login/")

        response = client.post(
            f"/requests_faculty/accept/{request.id}",
            {
                "departmentRoute": "True",
                "csrfmiddlewaretoken": client.cookies["csrftoken"].value,
            },
            HTTP_HOST=host,
            HTTP_X_FORWARDED_PROTO="https",
            HTTP_ORIGIN=f"https://{host}",
        )

        self.assertEqual(response.status_code, 302)
        request.refresh_from_db()
        self.assertEqual(request.status, StudentRequest.WAITING_FOR_DEPARTMENT)

    def test_plain_post_still_redirects(self):
        request = self.make_request(StudentRequest.WAITING_FOR_FACULTY)

        response = self.client.post(
            f"/requests_faculty/reject/{request.id}", HTTP_REFERER="/faculty/"
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/faculty/")

    def test_reject_no_longer_accepts_get(self):
        request = self.make_request(StudentRequest.WAITING_FOR_FACULTY)

        response = self.client.get(f"/requests_faculty/reject/{request.id}")

        self.assertEqual(response.status_code, 405)
        request.refresh_from_db()
        self.assertEqual(request.status, StudentRequest.WAITING_FOR_FACULTY)

    def test_approving_moves_the_request_from_awaiting_to_cleared(self):
        """The number a faculty can actually make move by approving.

        The approved-only headline cannot change here: approval routes the
        request onward rather than marking it used. The queue must.
        """
        request = self.make_request(
            StudentRequest.WAITING_FOR_FACULTY, datetime.date.today(), hours=2
        )
        before = self.client.get("/faculty/usage-summary", {"preset": "this_fy"}).json()

        self.client.post(
            f"/requests_faculty/accept/{request.id}",
            {"departmentRoute": "True"},
        )

        after = self.client.get("/faculty/usage-summary", {"preset": "this_fy"}).json()

        self.assertEqual(before["queue"]["awaiting_you"]["bookings"], 1)
        self.assertEqual(before["queue"]["cleared_by_you"]["bookings"], 0)
        self.assertEqual(after["queue"]["awaiting_you"]["bookings"], 0)
        self.assertEqual(after["queue"]["cleared_by_you"]["bookings"], 1)
        self.assertEqual(after["queue"]["cleared_by_you"]["hours"], 2.0)
        self.assertEqual(after["queue"]["with_department"]["bookings"], 1)
        # the headline is untouched: nothing has actually been used yet
        self.assertEqual(after["totals"], before["totals"])

    def test_usage_panel_is_rendered_for_faculty(self):
        # the panel is temporarily limited to the faculty trialling it
        self.faculty.email = "himanshu.aggarwal@hyderabad.bits-pilani.ac.in"
        self.faculty.save()

        response = self.client.get("/faculty/")

        self.assertContains(response, 'id="usagePanel"')
        self.assertContains(response, USAGE_URL)

    def test_slot_and_request_stay_consistent(self):
        request = self.make_request(StudentRequest.WAITING_FOR_FACULTY)
        self.client.post(f"/requests_faculty/reject/{request.id}")
        request.refresh_from_db()
        self.assertEqual(request.slot.status, Slot.STATUS_1)
