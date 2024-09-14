from django import template
from forms import settings


register = template.Library()

@register.simple_tag
def external_link_prefix():
    return settings.EXTERNAL_LINK_PREFIX