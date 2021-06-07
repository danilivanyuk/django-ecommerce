
from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def param_replace(context, **kwargs):
    d = context['request'].GET.copy()
    for k, v in kwargs.items():
        d[k] = v
    for k in [k for k, v in d.items() if not v]:
        del d[k]
    return d.urlencode()


def human_readable(value, arg):
    if hasattr(value, 'get_' + str(arg) + '_display'):
        return getattr(value, 'get_%s_display' % arg)()
    elif hasattr(value, str(arg)):
        if callable(getattr(value, str(arg))):
            return getattr(value, arg)()
        else:
            return getattr(value, arg)
    else:
        try:
            return value[arg]
        except KeyError:
            return settings.TEMPLATE_STRING_IF_INVALID


register.filter('human_readable', human_readable)
