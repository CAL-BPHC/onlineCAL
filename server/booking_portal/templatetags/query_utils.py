from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def update_query_params(context, **kwargs):
    """Adds to or updates the existing query parameters in a request."""
    query = context["request"].GET.copy()
    for k, v in kwargs.items():
        query[k] = v
    return query.urlencode()
