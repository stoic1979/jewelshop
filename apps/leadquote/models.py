from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from datetime import date

from django.db import models
from django.conf import settings


from autoslug import AutoSlugField

from apps.general.utils import custom_slugify


class JewelleryType(models.Model):
    """
    Jewellery listing...
    """
    jewellery_name = models.CharField(_('Jewelery'), max_length=255)
    jewellery_price = models.IntegerField(_('Price'), default=100)

    def __unicode__(self):
        return self.jewellery_name

    class Meta:

        verbose_name = 'Jewellery type'
        verbose_name_plural = 'Jewellery types'


class CustomerDetails(models.Model):
    """
    Customer details...
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='customer',
                             verbose_name="Related associate")
    first_name = models.CharField(_('First name'), max_length=255)
    last_name = models.CharField(_('Last name'), max_length=255)
    email = models.EmailField(_('Email address'), max_length=255)
    zip_code = models.CharField(_('Zip code'), max_length=6)
    email_slug_field = AutoSlugField(populate_from='email', slugify=custom_slugify, null=True, blank=True)
    country_select = models.CharField(_('Selected country'), max_length=255, null=True, blank=True)
    transaction_id = models.CharField(_('Transaction ID'), max_length=255, null=True, blank=True)

    def __unicode__(self):
        return "Customer::->>::-{0}".format(self.get_customer_full_name())

    class Meta:
        verbose_name = 'Customer detail'
        verbose_name_plural = 'Customer details'
        ordering = ['-id']

    def get_customer_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()


class JewelleryDetails(models.Model):
    """
    Jewellery details...
    """
    jewellery = models.ForeignKey(JewelleryType)
    jewellery_price = models.CharField(_('Price'), max_length=255)
    customer = models.ForeignKey(CustomerDetails, related_name='jewellery_detail',
                             verbose_name="Customer related jewellery")

    def __unicode__(self):
        return self.jewellery.jewellery_name

    class Meta:

        verbose_name = 'Jewellery detail'
        verbose_name_plural = 'Jewellery details'


class CustomerPremiumDetail(models.Model):
    """

    """
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Success', 'Success')
    )
    customer = models.ForeignKey(CustomerDetails, related_name='JewelryItems',
                             verbose_name="Premium customer", null=True, blank=True)
    selected_jewellery = models.ForeignKey(JewelleryType, related_name='jewellery_ttype')
    premium = models.CharField(_('Premium amount'), max_length=255)
    deduction = models.CharField(_('Deduction amount'), max_length=255)
    jewel_price = models.CharField(_('Jewellery price'), max_length=255)
    taxesAndSurcharges = models.CharField(_('Taxes And Surcharges'), max_length=255)
    notificationEmail = models.CharField(_('Notification Email'), max_length=255, null=True, blank=True)
    IsNotificationEmailSend = models.BooleanField(_('Is notification Email Send'), default=False)
    effectiveDate = models.DateField(_("Effective Date"), default=date.today)
    minTaxesAndSurcharges = models.CharField(_('Min Taxes And Surcharges'), max_length=255, null=True, blank=True)
    accountLocation = models.CharField(_('Account Location'), max_length=255, null=True, blank=True)
    isJewelersMutualPolicyholder = models.BooleanField(_('Jewelers Mutual Policy holder'), default=False)
    totalJewelryValue = models.CharField(_('Total Jewelry Value'), max_length=255, null=True, blank=True)
    safeConcealed = models.BooleanField(_('Safe Concealed'), default=False)
    safeAnchored = models.BooleanField(_('Safe Anchored'), default=False)
    safeWeightClass = models.CharField(_('Safe Weight Class'), max_length=255, null=True, blank=True, default=None)
    alarmType = models.CharField(_('Alarm Type'), max_length=255, null=True, blank=True, default=None)
    safeType = models.CharField(_('Safe Type'), max_length=255, null=True, blank=True, default=None)
    isEmailAlreadyUsed = models.BooleanField(_('Email Already Used'), default=False)
    isJewelersMutualCareTips = models.BooleanField(_('Is Jewelers Mutual Care Tips'), default=False)
    jewelerCode = models.CharField(_('Jeweler Code'), max_length=255, null=True, blank=True)
    isPlatinumPoints = models.BooleanField(_('Is Platinum Points'), default=False)
    emailAddress = models.CharField(_('Email Address'), max_length=255, null=True, blank=True)
    minPremium = models.CharField(_('Min Premium'), max_length=255, null=True, blank=True)
    status = models.CharField(_('Quote status'), max_length=255, choices=STATUS_CHOICES, default='Pending')

    def __unicode__(self):
        return "{0}>>>>{1}".format(self.customer.get_customer_full_name(), self.effectiveDate)

    class Meta:

        verbose_name = 'Customer premium detail'
        verbose_name_plural = 'Customer premium details'
