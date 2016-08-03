from django.contrib import admin
from apps.profile.models import StoreAccountProfile, AssociateAccountProfile, StoreAssociateAccount, AdminStoreAccount


admin.site.register(StoreAccountProfile)
admin.site.register(AssociateAccountProfile)
admin.site.register(StoreAssociateAccount)
admin.site.register(AdminStoreAccount)
