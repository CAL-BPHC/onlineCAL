from urllib.parse import urlparse

from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder, Layout, Submit
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django_filters import DateFilter, FilterSet, OrderingFilter

from ... import forms, models


def safe_portal_url(candidate, request, portal):
    """`candidate` if it is that portal's own page on this site, else the portal.

    Keeps the filter and page a reviewer was on when they opened an
    application, without letting a crafted value bounce them off site or onto
    a portal their role cannot open.
    """
    fallback = reverse(portal)
    if candidate and url_has_allowed_host_and_scheme(
        candidate,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        path = urlparse(candidate).path
        if path.rstrip("/") == fallback.rstrip("/"):
            return candidate
    return fallback


def portal_return_url(request, portal):
    """Where a decision returns to: the list it was made from, or the portal."""
    return safe_portal_url(
        request.POST.get("next") or request.META.get("HTTP_REFERER"), request, portal
    )


def active_filter_scope(portal_filter):
    """What the portal filter is currently showing.

    Handing this to the template keeps the parameter names owned by the
    filterset, instead of the panel's JavaScript re-deriving them from the URL.
    """
    data = portal_filter.form.data
    return {
        name: data.get(name, "")
        for name in ("status", "instrument", "from_date", "to_date")
    }


def get_pagintion_nav_range(page_obj):
    begin = page_obj.number - 5
    end = page_obj.number + 4
    offset = -begin + 1 if begin < 1 else 1

    begin += offset
    end += offset
    end = page_obj.paginator.num_pages if end > page_obj.paginator.num_pages else end
    return range(begin, end + 1)


class BasePortalFilter(FilterSet):
    """Filters on user requests portal"""

    PORTAL_PAGE_SIZE = 25

    from_date = DateFilter(
        field_name="slot__date",
        lookup_expr=("gte"),
        label="From",
        widget=forms.DateInput,
    )
    to_date = DateFilter(
        field_name="slot__date",
        lookup_expr=("lte"),
        label="To",
        widget=forms.DateInput,
    )

    # (model field, url parameter). Keeping the parameter identical to the field
    # name preserves existing ?order=slot__date links; the previous pairing was
    # reversed and silently ordered by the slot foreign key instead of the date.
    order = OrderingFilter(
        fields=(("slot__date", "slot__date"),),
        field_labels={"slot__date": "Slot date"},
    )

    def __init__(self, *args, **kwargs):
        self.student_queryset = kwargs.pop("student_queryset", None)
        self.faculty_queryset = kwargs.pop("faculty_queryset", None)
        super().__init__(*args, **kwargs)

        # Meta.model is StudentRequest, but this filterset also runs against
        # FacultyRequest querysets, which have no "waiting for faculty approval"
        # status. Offering it there gives an option that can never match.
        model = getattr(self.queryset, "model", None)
        if model is not None and model is not models.StudentRequest:
            self.filters["status"].extra["choices"] = model.STATUS_CHOICES

    @staticmethod
    def apply_filter(queryset, field, value):
        if field == "from_date":
            return queryset.filter(slot__date__gte=value)
        elif field == "to_date":
            return queryset.filter(slot__date__lte=value)
        else:
            return queryset.filter(**{f"{field}__exact": value})

    @property
    def qs(self):
        # For department portal, we need to filter on both student and faculty requests
        # Django doesn't support filtering on union queryset directly
        if (
            self.student_queryset is not None
            and self.faculty_queryset is not None
            and self.form.is_valid()
        ):
            student_filtered = self.student_queryset
            faculty_filtered = self.faculty_queryset
            cleaned_data = {k: v for k, v in self.form.cleaned_data.items() if v}
            order_by = cleaned_data.pop("order", ["-slot__date"])
            for field, value in cleaned_data.items():
                student_filtered = BasePortalFilter.apply_filter(
                    student_filtered, field, value
                )
                faculty_filtered = BasePortalFilter.apply_filter(
                    faculty_filtered, field, value
                )
            return student_filtered.union(faculty_filtered).order_by(*order_by)
        return super().qs

    @property
    def form(self):
        form = super().form
        helper = FormHelper(form)
        helper.form_class = "form-horizontal"
        helper.field_class = "col-8"
        helper.label_class = "col-4"
        helper.form_method = "GET"
        helper.layout = Layout(
            "status",
            "instrument",
            "from_date",
            "to_date",
            "order",
            ButtonHolder(
                Submit(
                    "apply", value="Apply", css_class="btn btn-primary mx-auto d-block"
                )
            ),
        )
        form.helper = helper
        return form

    def paginate(self):
        paginator = Paginator(self.qs, self.PORTAL_PAGE_SIZE)
        page = self.data.get("page", 1)
        try:
            return paginator.page(page)
        except PageNotAnInteger:
            return paginator.page(1)
        except EmptyPage:
            return paginator.page(paginator.num_pages)

    class Meta:
        model = models.StudentRequest
        fields = {
            "status": ["exact"],
            "instrument": ["exact"],
        }
