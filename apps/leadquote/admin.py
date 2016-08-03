from django.contrib import admin
from apps.leadquote.models import JewelleryType, CustomerDetails, JewelleryDetails, CustomerPremiumDetail


admin.site.register(JewelleryType)
admin.site.register(CustomerDetails)
admin.site.register(JewelleryDetails)
admin.site.register(CustomerPremiumDetail)