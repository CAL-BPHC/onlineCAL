from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Submit
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django_filters import (
    FilterSet,
    DateFilter,
    OrderingFilter,
)

from ... import models
from ... import forms


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
        model = models.Request
        fields = {
            "status": ["exact"],
            "instrument": ["exact"],
        }
