from django import template


register = template.Library()

@register.filter
def split_group_name(name):
    return name.split("_")[-1]