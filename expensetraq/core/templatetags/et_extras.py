from django import template

register = template.Library()


@register.filter
def is_in_groups(user):
    return {g.name for g in user.groups.all()}
