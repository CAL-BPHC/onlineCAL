from crispy_forms.exceptions import CrispyError
from crispy_forms.utils import get_template_pack
from django import template
from django.template import Context, loader

register = template.Library()


@register.simple_tag()
def bs4_appended_prepended_text(field, append="", prepend="", form_show_labels=True):
    """
    Similar to the `crispy_addon` tag. However, this one respects classes that
    have been set in the corresponding Form layout object.
    """

    template_pack = get_template_pack()
    if template_pack != "bootstrap4":
        raise CrispyError(
            "bs4_appended_prepended_text can only be used with Bootstrap 4"
        )

    if field:
        attributes = {
            "field": field,
            "form_show_errors": True,
            "form_show_labels": form_show_labels,
        }
        helper = getattr(field.form, "helper", None)
        if helper is not None:
            attributes.update(helper.get_attributes(get_template_pack()))

        context = Context(attributes)
        template = loader.get_template(
            "%s/layout/prepended_appended_text.html" % get_template_pack()
        )
        context["crispy_prepended_text"] = prepend
        context["crispy_appended_text"] = append

        if not prepend and not append:
            raise TypeError("Expected a prepend and/or append argument")

        context = context.flatten()

    return template.render(context)
