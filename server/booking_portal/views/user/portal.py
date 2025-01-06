from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder, Layout, Submit
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django_filters import DateFilter, FilterSet, OrderingFilter

from ... import forms, models


def get_pagintion_nav_range(page_obj):
    begin = page_obj.number - 5
    end = page_obj.number + 4
    offset = -begin + 1 if begin < 1 else 1

    begin += offset
    end += offset
    end = page_obj.paginator.num_pages if end > page_obj.paginator.num_pages else end
    return range(begin, end)


class BasePortalFilter(FilterSet):
    """Filters on user requests portal"""

    PORTAL_PAGE_SIZE = 25

    from_date = DateFilter(
        field_name="slot__date",
        lookup_expr=("gt"),
        label="From",
        widget=forms.DateInput(attrs={"class": "datepicker"}),
    )
    to_date = DateFilter(
        field_name="slot__date",
        lookup_expr=("lt"),
        label="To",
        widget=forms.DateInput(attrs={"class": "datepicker"}),
    )

    order = OrderingFilter(fields=(("slot", "slot__date"),))

    def __init__(self, *args, **kwargs):
        self.student_queryset = kwargs.pop("student_queryset", None)
        self.faculty_queryset = kwargs.pop("faculty_queryset", None)
        super().__init__(*args, **kwargs)

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
