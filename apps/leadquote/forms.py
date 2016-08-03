import math
import uuid
from django import forms
from django.forms import modelformset_factory
from django.forms.models import BaseModelFormSet


from apps.leadquote.models import CustomerDetails, JewelleryDetails
from apps.general.utils import custom_slugify, random_word, get_hex_string


class CustomerDetailsForm(forms.ModelForm):
    # country_select = forms.ChoiceField(label=u'Country select', widget=forms.RadioSelect())

    class Meta:
        model = CustomerDetails
        fields = ['first_name', 'last_name',
                  'email', 'zip_code', 'country_select']

    def __init__(self, countries=None, *args, **kwargs):
        super(CustomerDetailsForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control input-lg'
            self.fields['first_name'].widget.attrs['placeholder'] = 'First Name'
            self.fields['last_name'].widget.attrs['placeholder'] = 'Last Name'
            self.fields['email'].widget.attrs['placeholder'] = 'Email Address'
            self.fields['zip_code'].widget.attrs['placeholder'] = 'Zip'
            self.fields['zip_code'].widget.attrs['class'] = 'form-control input-lg zip_code'

    def save(self, user, commit=True, country_select=None, *args, **kwargs):
        customer = super(CustomerDetailsForm, self).save(commit=False)
        if commit:
            print " commit------------------"
            customer.user = user
            if country_select:
                customer.country_select = country_select
                customer.transaction_id = str(uuid.uuid4())
            customer.save()
        return customer


class JewelleryDetailsForm(forms.ModelForm):

    class Meta:
        model = JewelleryDetails
        fields = ['jewellery', 'jewellery_price',]

    def __init__(self, countries=None, *args, **kwargs):
        super(JewelleryDetailsForm, self).__init__(*args, **kwargs)
        self.fields['jewellery'].widget.attrs['class'] = 'form-control jewelType'
        self.fields['jewellery_price'].widget.attrs['class'] = 'form-control input-lg jewelRate'
        self.fields['jewellery'].empty_label = "Select a Type"

    def clean_jewellery_price(self):
        jewellery_vale = self.cleaned_data.get("jewellery_price")
        price = float(jewellery_vale)
        if math.isnan(price):
            raise forms.ValidationError("Enter a valid number")
        else:
            jewellery_price = int(math.ceil(price))
        return jewellery_price


class BaseJewelleryDetailsFormset(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        super(BaseJewelleryDetailsFormset, self).__init__(*args, **kwargs)
        self.queryset = JewelleryDetails.objects.none()

JewelleryDetailsFormSet = modelformset_factory(JewelleryDetails,
                                               form=JewelleryDetailsForm, formset=BaseJewelleryDetailsFormset)