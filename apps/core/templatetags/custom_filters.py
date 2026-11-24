from django import template

register = template.Library()

@register.filter(name='dict_key')
def dict_key(d, key):
    """Retrieves dictionary value by key."""
    if isinstance(d, dict):
        return d.get(key, '')
    return ''
