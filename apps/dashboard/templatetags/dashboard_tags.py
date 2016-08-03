from django import template
register = template.Library()

from apps.profile.models import StoreAssociateAccount

@register.assignment_tag
def get_store_associate_acc(associate):
    try:
        store_associate_acc = StoreAssociateAccount.objects.get(user=associate)
    except:
        store_associate_acc = None
    return store_associate_acc

@register.assignment_tag
def is_quote(associate):
    status = True
    quote_list = []
    for customer in associate.customer.all():
        for quote in customer.JewelryItems.all():
            if quote:
                quote_list.append(quote)
    if len(quote_list) < 1:
        status = False
    return status
