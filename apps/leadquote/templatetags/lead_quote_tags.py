from django import template
from apps.leadquote.models import JewelleryType

register = template.Library()


@register.filter(name='jewel_name')
def jewel_name(jewel, jewel_id):
    jewellery_name = ''
    try:
        jewellery = JewelleryType.objects.get(pk=int(jewel_id))
    except:
        jewellery = None
    if jewellery:
        jewellery_name = jewellery.jewellery_name.strip()
    return jewellery_name

@register.filter(name='zipped_list')
def zipped_list(jewelryItem):
    premiums = jewelryItem.get('premiums')
    deductibles = jewelryItem.get('deductibles')
    taxesAndSurcharges = jewelryItem.get('taxesAndSurcharges')
    premiums_deductibles = zip(premiums, deductibles, taxesAndSurcharges)
    print "premiums_deductibles", premiums_deductibles
    return premiums_deductibles
