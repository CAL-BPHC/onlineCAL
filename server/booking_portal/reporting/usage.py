"""Usage aggregation for the faculty portal panel.

Cost lives in a Python property on the request models (it depends on the
generic form object and on the additional_charges JSON), so none of this can be
pushed into the database with annotate(). Rows are fetched with their relations
and reduced in Python, the same way the admin usage reports do it.
"""

import calendar
import datetime

from django.core.exceptions import ObjectDoesNotExist

from ..models.faculty_request import FacultyRequest
from ..models.request import StudentRequest

# Indian financial year: 1 April to 31 March.
FY_START_MONTH = 4

PRESETS = ("this_fy", "last_fy", "last_3_months", "this_month", "all_time", "custom")
DEFAULT_PRESET = "this_fy"

OWN_BOOKING_LABEL = "My own bookings"

# A rejected or cancelled booking never happened, so it can never add to a
# usage figure, whatever the portal filter happens to be showing.
NON_USAGE_STATUSES = frozenset({StudentRequest.REJECTED, StudentRequest.CANCELLED})

# The statuses either the totals or the approval queue can care about. Anything
# else would be fetched and hydrated for nothing.
LIVE_STATUSES = (
    StudentRequest.WAITING_FOR_FACULTY,
    StudentRequest.WAITING_FOR_LAB_ASST,
    StudentRequest.WAITING_FOR_DEPARTMENT,
    StudentRequest.APPROVED,
)

_CLEARED_STATUSES = frozenset(
    {
        StudentRequest.WAITING_FOR_LAB_ASST,
        StudentRequest.WAITING_FOR_DEPARTMENT,
        StudentRequest.APPROVED,
    }
)

# total_cost walks a generic relation and a JSON blob; historical rows with
# missing or malformed form data must not take a report or the panel down.
_COST_ERRORS = (
    ObjectDoesNotExist,
    AttributeError,
    KeyError,
    TypeError,
    ZeroDivisionError,
)


def safe_total_cost(request, default=0.0):
    """total_cost, or `default` when the request's form data is unusable.

    Callers that sum want a number; the CSV export wants a blank cell, so that
    an unpriced row is not mistaken for a free one.
    """
    try:
        return float(request.total_cost or 0)
    except _COST_ERRORS:
        return default


def request_hours(request):
    """Length of a request's slot, in hours."""
    try:
        return request.slot.duration.total_seconds() / 3600
    except (AttributeError, TypeError):
        return 0.0


def financial_year_bounds(on_date=None):
    """Return (start, end) of the financial year containing `on_date`."""
    on_date = on_date or datetime.date.today()
    year = on_date.year if on_date.month >= FY_START_MONTH else on_date.year - 1
    start = datetime.date(year, FY_START_MONTH, 1)
    end = datetime.date(year + 1, FY_START_MONTH, 1) - datetime.timedelta(days=1)
    return start, end


def financial_year_label(start):
    """'FY 25-26' for a financial year starting in 2025."""
    return "FY {:02d}-{:02d}".format(start.year % 100, (start.year + 1) % 100)


def status_label(status):
    """Human name for a status, without the inconsistent trailing full stops."""
    return dict(StudentRequest.STATUS_CHOICES).get(status, status).rstrip(".")


def _shift_months(date, months):
    month_index = date.month - 1 - months
    year = date.year + month_index // 12
    month = month_index % 12 + 1
    return date.replace(
        year=year, month=month, day=min(date.day, calendar.monthrange(year, month)[1])
    )


def resolve_range(preset=None, start=None, end=None, today=None):
    """Turn a preset (or an explicit custom range) into (start, end, label).

    `start`/`end` may be None, which means unbounded on that side.
    """
    today = today or datetime.date.today()
    preset = preset or DEFAULT_PRESET

    if preset == "custom":
        if start and end and start > end:
            start, end = end, start
        if start and end:
            label = "{:%d %b %Y} - {:%d %b %Y}".format(start, end)
        elif start:
            label = "From {:%d %b %Y}".format(start)
        elif end:
            label = "Up to {:%d %b %Y}".format(end)
        else:
            label = "Custom range"
        return start, end, label

    if preset == "all_time":
        return None, None, "All time"

    if preset == "this_month":
        month_start = today.replace(day=1)
        month_end = month_start.replace(
            day=calendar.monthrange(month_start.year, month_start.month)[1]
        )
        return month_start, month_end, month_start.strftime("%B %Y")

    if preset == "last_3_months":
        return _shift_months(today, 3), today, "Last 3 months"

    fy_start, fy_end = financial_year_bounds(today)
    if preset == "last_fy":
        fy_start, fy_end = financial_year_bounds(fy_start - datetime.timedelta(days=1))
    return fy_start, fy_end, financial_year_label(fy_start)


def _new_bucket(key, with_children=False):
    bucket = {"key": key, "hours": 0.0, "cost": 0.0, "bookings": 0}
    if with_children:
        bucket["children"] = {}
    return bucket


def _add(store, key, hours, cost, with_children=False):
    bucket = store.get(key)
    if bucket is None:
        bucket = store[key] = _new_bucket(key, with_children)
    bucket["hours"] += hours
    bucket["cost"] += cost
    bucket["bookings"] += 1
    return bucket


def _rounded(bucket):
    return {
        "key": bucket["key"],
        "hours": round(bucket["hours"], 2),
        "cost": round(bucket["cost"], 2),
        "bookings": bucket["bookings"],
    }


def _serialise(store):
    """Flatten the nested accumulators into JSON friendly rows, biggest first."""
    rows = []
    for bucket in store.values():
        row = _rounded(bucket)
        row["children"] = sorted(
            (_rounded(child) for child in bucket["children"].values()),
            key=lambda child: (-child["hours"], child["key"]),
        )
        rows.append(row)
    rows.sort(key=lambda row: (-row["hours"], row["key"]))
    return rows


def _empty_queue():
    return {
        name: _new_bucket(name)
        for name in ("awaiting_you", "cleared_by_you", "with_department", "with_lab")
    }


def collect_usage(faculty, start=None, end=None, instrument=None, status=None):
    """Aggregate one faculty's usage between two dates (both inclusive).

    An instrument or status narrows the totals and breakdown, which is how the
    panel follows the portal's own filter and shows whichever slice the faculty
    is looking at. Rejected and cancelled bookings are the exception: they are
    never summed, because that time was never spent.

    Without a status the totals cover approved bookings only. The approval
    queue reported alongside them follows the same range and instrument, but
    not the status: the queue is itself a breakdown by status, so narrowing it
    to one would leave every other bucket permanently empty. Both come out of
    one walk over the faculty's requests: resolving cost means hydrating a
    generic relation per row, so scanning that history twice per request would
    double the expensive half of this.
    """
    status = status or StudentRequest.APPROVED
    counts_towards_usage = status not in NON_USAGE_STATUSES
    instrument = int(instrument) if instrument else None

    student_requests = (
        StudentRequest.objects.filter(faculty=faculty, status__in=LIVE_STATUSES)
        .select_related("slot", "instrument", "student")
        .prefetch_related("content_object")
    )
    # The faculty's own bookings never enter the approval queue, so unlike the
    # student requests they can be narrowed in SQL.
    own_requests = FacultyRequest.objects.none()
    if counts_towards_usage:
        own_requests = FacultyRequest.objects.filter(
            faculty=faculty, status=status
        ).select_related("slot", "instrument")
        if start:
            own_requests = own_requests.filter(slot__date__gte=start)
        if end:
            own_requests = own_requests.filter(slot__date__lte=end)
        if instrument:
            own_requests = own_requests.filter(instrument_id=instrument)
        own_requests = own_requests.prefetch_related("content_object")

    queue = _empty_queue()
    totals = _new_bucket("totals")
    by_instrument = {}
    by_student = {}

    def in_scope(request):
        date = request.slot.date
        if start and date < start:
            return False
        if end and date > end:
            return False
        return not (instrument and request.instrument_id != instrument)

    def record(request, who, hours, cost):
        name = request.instrument.name
        totals["hours"] += hours
        totals["cost"] += cost
        totals["bookings"] += 1
        _add(_add(by_instrument, name, hours, cost, True)["children"], who, hours, cost)
        _add(_add(by_student, who, hours, cost, True)["children"], name, hours, cost)

    for request in student_requests:
        if not in_scope(request):
            continue

        hours = request_hours(request)
        cost = safe_total_cost(request)

        if request.status == StudentRequest.WAITING_FOR_FACULTY:
            _add(queue, "awaiting_you", hours, cost)
        elif request.status in _CLEARED_STATUSES:
            _add(queue, "cleared_by_you", hours, cost)
            if request.status == StudentRequest.WAITING_FOR_DEPARTMENT:
                _add(queue, "with_department", hours, cost)
            elif request.status == StudentRequest.WAITING_FOR_LAB_ASST:
                _add(queue, "with_lab", hours, cost)

        if counts_towards_usage and request.status == status:
            record(request, str(request.student), hours, cost)

    for request in own_requests:
        record(
            request, OWN_BOOKING_LABEL, request_hours(request), safe_total_cost(request)
        )

    return {
        "basis": {
            "status": status,
            "label": status_label(status),
            "is_approved": status == StudentRequest.APPROVED,
            "counts_towards_usage": counts_towards_usage,
        },
        "totals": {
            "hours": round(totals["hours"], 2),
            "cost": round(totals["cost"], 2),
            "bookings": totals["bookings"],
        },
        "queue": {name: _rounded(bucket) for name, bucket in queue.items()},
        "by_instrument": _serialise(by_instrument),
        "by_student": _serialise(by_student),
    }


def approval_queue(faculty, start=None, end=None, instrument=None):
    """The faculty's approval workload over a range, defaulting to all of it."""
    return collect_usage(faculty, start, end, instrument)["queue"]
