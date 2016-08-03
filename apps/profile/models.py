from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.db import models
from django.conf import settings

from cities_light.models import Country


class StoreAccountProfile(models.Model):
    """
    Store account profile
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='store_acc_profile',
                                verbose_name="Store account Profile")
    store_name = models.CharField(_('Store Name'), max_length=255)
    jew_id = models.CharField(_('Jeweller ID'), max_length=255, unique=True)
    lear_lab_ID = models.CharField(_('Lear lab ID'), max_length=255, unique=True)
    store_address = models.TextField(_('Store Address'))
    city = models.CharField(_('City'), max_length=255)
    state = models.CharField(_('State'), max_length=255)
    zip_code = models.CharField(_('Store Zip Code'), max_length=7)
    country = models.ForeignKey(Country, verbose_name='Store country')
    phone = models.CharField(_('Store Phone'), max_length=12)
    store_pic = models.ImageField(_('Store photo'), upload_to="store_profile_pic", null=True, blank=True)
    website = models.URLField(_('Store website'), max_length=255)

    def __unicode__(self):
        return self.user.get_full_name()

    class Meta:
        verbose_name = 'Store account profile'
        verbose_name_plural = 'Store account profiles'


class AssociateAccountProfile(models.Model):
    """
    Associate account profile
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='associate_acc_profile',
                                verbose_name="Store account Profile")
    designation = models.CharField(_('Designation'), max_length=255)
    phone = models.CharField(_('Phone'), max_length=12)
    zip_code = models.CharField(_('Zipcode'), max_length=7)
    address = models.TextField(_('Address'))
    associate_photo = models.ImageField(_('Associate photo'),
                                        upload_to="associate_profile_pics", null=True, blank=True)
    associate_code = models.CharField(_('Associate Code'), max_length=6)

    def __unicode__(self):
        return self.user.get_full_name()

    class Meta:

        verbose_name = 'Associate account profile'
        verbose_name_plural = 'Associates account profiles'


class StoreAssociateAccount(models.Model):
    """
    Store admin linked Associate account profile
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='associate_acc',
                                verbose_name="Associate account Profile")
    store_account = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='created_store',
                                      verbose_name="Store account")

    def __unicode__(self):
        return "{0}::->>::-{1}".format(self.store_account.get_full_name(), self.user.get_full_name())

    class Meta:

        verbose_name = 'Store linked Associate account'
        verbose_name_plural = 'Store linked Associate account'


class AdminStoreAccount(models.Model):
    """
    Super admin linked store accounts
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='store_acc',
                                verbose_name="Store account Profile")
    super_admin_account = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='super_admin',
                                      verbose_name="Admin account")

    def __unicode__(self):
        return self.super_admin_account.get_full_name()

    class Meta:

        verbose_name = 'Admin linked store account'
        verbose_name_plural = 'Admin linked store account'




