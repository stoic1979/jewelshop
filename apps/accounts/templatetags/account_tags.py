from django import template
from django.contrib.auth.models import Group

register = template.Library()


@register.filter(name='has_group')
def has_group(user, group_name):
    try:
        is_user_exists = user.groups.filter(name=group_name).exists()
    except:
        is_user_exists = False
    return is_user_exists

@register.simple_tag
def store_percent_amount(total, store_amount):
    percentage = (float(store_amount)*100/float(total))
    return percentage
