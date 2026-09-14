from django import template

register = template.Library()


@register.filter(is_safe=False)
def subtract(value, arg):
    """Subtract the arg to the value."""
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        try:
            return value + arg
        except Exception:  # noqa: BLE001 - a filter must never raise
            return ""
