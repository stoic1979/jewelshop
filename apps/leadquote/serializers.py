import datetime
import ast

from decimal import Decimal

from rest_framework import serializers
from .models import CustomerDetails, CustomerPremiumDetail, JewelleryType
from apps.profile.models import StoreAssociateAccount
from collections import OrderedDict


class JewelleryTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = JewelleryType
        fields = ('id', )


class PremiumSerializer(serializers.ModelSerializer):

    ActualPurchasePrice = serializers.SerializerMethodField('get_price')
    RetailReplacementValue = serializers.SerializerMethodField('get_price')
    MinimiumAllowedReplacementValue = serializers.SerializerMethodField('get_min_replacement_value')
    MaximumAllowedReplacementvalue = serializers.SerializerMethodField('get_max_replacement_value')
    Premium = serializers.SerializerMethodField('get_premium')
    Deductible = serializers.SerializerMethodField('get_deduction')
    Adjustment = serializers.SerializerMethodField('get_adjustment_value')
    Quantity = serializers.SerializerMethodField('get_quantity_value')
    TaxAndSurcharge = serializers.SerializerMethodField('get_taxesAndSurcharges')
    JewelryType = serializers.SerializerMethodField('get_selected_jewellery')
    Description = serializers.SerializerMethodField('get_description')
    ExtendedDescription = serializers.SerializerMethodField('get_description')
    AppraisalDate = serializers.SerializerMethodField('get_appraisal_date')

    class Meta:
        model = CustomerPremiumDetail
        fields = ('ActualPurchasePrice', 'RetailReplacementValue',
                  'MinimiumAllowedReplacementValue', 'MaximumAllowedReplacementvalue',
                  'Premium', 'Deductible', 'TaxAndSurcharge', 'Adjustment', 'Quantity',
                  'Description', 'ExtendedDescription', 'JewelryType', 'AppraisalDate'
                  )

    def get_price(self, obj):
        return Decimal(obj.jewel_price)

    def get_premium(self, obj):
        return Decimal(obj.premium)

    def get_deduction(self, obj):
        return Decimal(obj.deduction)

    def get_selected_jewellery(self, obj):
        return obj.selected_jewellery.id

    def get_taxesAndSurcharges(self, obj):
        return Decimal(obj.taxesAndSurcharges)

    def get_jewel_price(self, obj):
        return Decimal(obj.jewel_price)

    def get_min_replacement_value(self, obj):
        return 0

    def get_max_replacement_value(self, obj):
        return None

    def get_adjustment_value(self, obj):
        return 0

    def get_quantity_value(self, obj):
        return 1

    def get_description(self, obj):
        return obj.selected_jewellery.jewellery_name

    def get_appraisal_date(self, obj):
        return datetime.datetime.now()


class CustomerSerializer(serializers.ModelSerializer):

    FileNames = serializers.SerializerMethodField('get_fileNames')
    JewelryItems = PremiumSerializer(many=True, read_only=True)
    Applicant = serializers.SerializerMethodField('get_applicant')
    JewelryPurchaseKeys = serializers.SerializerMethodField('get_PurchaseKeys')
    DistributionSource = serializers.SerializerMethodField('get_distributionSource')
    GuidewireLinkId = serializers.SerializerMethodField('get_guidewireLinkId')
    CorrelationId = serializers.SerializerMethodField('get_correlationId')
    IsPolicySubmission = serializers.SerializerMethodField('get_isPolicySubmission')
    JewelerName = serializers.SerializerMethodField('get_jewelerName')
    HasExpired = serializers.SerializerMethodField('get_hasExpired')
    ProgramDescription = serializers.SerializerMethodField('get_programDescription')

    class Meta:
        model = CustomerDetails
        fields = ('Applicant', 'FileNames', 'JewelryItems', 'JewelryPurchaseKeys', 'DistributionSource', 'GuidewireLinkId',
                  'CorrelationId', 'IsPolicySubmission', 'JewelerName', 'HasExpired', 'ProgramDescription')

    def get_fileNames(self, obj):
        return None

    def get_mailingAddress(self, obj):
        return None

    def get_applicant(self, obj):
        data = ast.literal_eval(obj.country_select)
        if data.get('country') == 0:
            country_name = 'US'
        elif data.get('country') == 1:
            country_name = 'CA'
        else:
             country_name = 'US'

        residence_address = OrderedDict([
                                        ("Address1", "***Enter Address***"),
                                        ("Address2", ""),
                                        ("City", "***Enter City***"),
                                        ("State", data.get('state')),
                                        ("PostalCode", obj.zip_code),
                                        ("County", data.get('county')),
                                        ("Country", country_name)
                                        ])

        details = OrderedDict([
            ("FirstName", obj.first_name),
            ("LastName", obj.last_name),
            ("PrimaryPhone", ""),
            ("Email", obj.email),
            ("ResidenceAddress", residence_address),
            ("MailingAddress", None),
             ])
        return details

    def get_residence_address(self, obj):
        data = ast.literal_eval(obj.country_select)
        if data.get('country') == 0:
            country_name = 'US'
        elif data.get('country') == 1:
            country_name = 'CA'
        else:
             country_name = 'US'

        residence_address = OrderedDict([
                        ("Address1", "***Enter Address***"),
                        ("Address2", ""),
                        ("City", "***Enter City***"),
                        ("State", data.get('state')),
                        ("PostalCode", obj.zip_code),
                        ("County", data.get('county')),
                        ("Country",country_name) ])
        return residence_address

    def get_primaryPhone(self, obj):
        return ""

    def get_programDescription(self, obj):
        return "AgnosticPOS"

    def get_hasExpired(self, obj):
        return False

    def get_jewelerName(self, obj):
        store = StoreAssociateAccount.objects.get(user=obj.user)
        return store.store_account.store_acc_profile.store_name

    def get_isPolicySubmission(self, obj):
        return False

    def get_correlationId(self, obj):
        return " "

    def get_guidewireLinkId(self, obj):
        return "cm:1234"

    def get_distributionSource(self, obj):
        return 4

    def get_first_name(self, obj):
        return obj.first_name

    def get_last_name(self, obj):
        return obj.last_name

    def get_email(self, obj):
        return obj.email

    def get_zip_code(self, obj):
        return obj.zip_code

    def get_transaction_id(self, obj):
        return obj.transaction_id

    def get_jewel_items(self, obj):
        return PremiumSerializer(many=True, read_only=True)

    def get_PurchaseKeys(self, obj):

        listing = [OrderedDict([("FieldType", 1),
                              ("DisplayName", ""),
                              ("Name", "uniqueid"),
                              ("Value", obj.transaction_id)
                              ])]
        return listing


