# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import autoslug.fields
import datetime
from django.conf import settings
import apps.general.utils


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerDetails',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(max_length=255, verbose_name='First name')),
                ('last_name', models.CharField(max_length=255, verbose_name='Last name')),
                ('email', models.EmailField(max_length=255, verbose_name='Email address')),
                ('zip_code', models.CharField(max_length=6, verbose_name='Zip code')),
                ('email_slug_field', autoslug.fields.AutoSlugField(editable=False, populate_from='email', blank=True, null=True, slugify=apps.general.utils.custom_slugify)),
                ('country_select', models.CharField(max_length=255, null=True, verbose_name='Selected country', blank=True)),
                ('transaction_id', models.CharField(max_length=255, null=True, verbose_name='Transaction ID', blank=True)),
                ('user', models.ForeignKey(related_name='customer', verbose_name='Related associate', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-id'],
                'verbose_name': 'Customer detail',
                'verbose_name_plural': 'Customer details',
            },
        ),
        migrations.CreateModel(
            name='CustomerPremiumDetail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('premium', models.CharField(max_length=255, verbose_name='Premium amount')),
                ('deduction', models.CharField(max_length=255, verbose_name='Deduction amount')),
                ('jewel_price', models.CharField(max_length=255, verbose_name='Jewellery price')),
                ('taxesAndSurcharges', models.CharField(max_length=255, verbose_name='Taxes And Surcharges')),
                ('notificationEmail', models.CharField(max_length=255, null=True, verbose_name='Notification Email', blank=True)),
                ('IsNotificationEmailSend', models.BooleanField(default=False, verbose_name='Is notification Email Send')),
                ('effectiveDate', models.DateField(default=datetime.date.today, verbose_name='Effective Date')),
                ('minTaxesAndSurcharges', models.CharField(max_length=255, null=True, verbose_name='Min Taxes And Surcharges', blank=True)),
                ('accountLocation', models.CharField(max_length=255, null=True, verbose_name='Account Location', blank=True)),
                ('isJewelersMutualPolicyholder', models.BooleanField(default=False, verbose_name='Jewelers Mutual Policy holder')),
                ('totalJewelryValue', models.CharField(max_length=255, null=True, verbose_name='Total Jewelry Value', blank=True)),
                ('safeConcealed', models.BooleanField(default=False, verbose_name='Safe Concealed')),
                ('safeAnchored', models.BooleanField(default=False, verbose_name='Safe Anchored')),
                ('safeWeightClass', models.CharField(default=None, max_length=255, null=True, verbose_name='Safe Weight Class', blank=True)),
                ('alarmType', models.CharField(default=None, max_length=255, null=True, verbose_name='Alarm Type', blank=True)),
                ('safeType', models.CharField(default=None, max_length=255, null=True, verbose_name='Safe Type', blank=True)),
                ('isEmailAlreadyUsed', models.BooleanField(default=False, verbose_name='Email Already Used')),
                ('isJewelersMutualCareTips', models.BooleanField(default=False, verbose_name='Is Jewelers Mutual Care Tips')),
                ('jewelerCode', models.CharField(max_length=255, null=True, verbose_name='Jeweler Code', blank=True)),
                ('isPlatinumPoints', models.BooleanField(default=False, verbose_name='Is Platinum Points')),
                ('emailAddress', models.CharField(max_length=255, null=True, verbose_name='Email Address', blank=True)),
                ('minPremium', models.CharField(max_length=255, null=True, verbose_name='Min Premium', blank=True)),
                ('status', models.CharField(default='Pending', max_length=255, verbose_name='Quote status', choices=[('Pending', 'Pending'), ('Success', 'Success')])),
                ('customer', models.ForeignKey(related_name='JewelryItems', verbose_name='Premium customer', blank=True, to='leadquote.CustomerDetails', null=True)),
            ],
            options={
                'verbose_name': 'Customer premium detail',
                'verbose_name_plural': 'Customer premium details',
            },
        ),
        migrations.CreateModel(
            name='JewelleryDetails',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('jewellery_price', models.CharField(max_length=255, verbose_name='Price')),
                ('customer', models.ForeignKey(related_name='jewellery_detail', verbose_name='Customer related jewellery', to='leadquote.CustomerDetails')),
            ],
            options={
                'verbose_name': 'Jewellery detail',
                'verbose_name_plural': 'Jewellery details',
            },
        ),
        migrations.CreateModel(
            name='JewelleryType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('jewellery_name', models.CharField(max_length=255, verbose_name='Jewelery')),
                ('jewellery_price', models.IntegerField(default=100, verbose_name='Price')),
            ],
            options={
                'verbose_name': 'Jewellery type',
                'verbose_name_plural': 'Jewellery types',
            },
        ),
        migrations.AddField(
            model_name='jewellerydetails',
            name='jewellery',
            field=models.ForeignKey(to='leadquote.JewelleryType'),
        ),
        migrations.AddField(
            model_name='customerpremiumdetail',
            name='selected_jewellery',
            field=models.ForeignKey(related_name='jewellery_ttype', to='leadquote.JewelleryType'),
        ),
    ]
