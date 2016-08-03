from django.forms import ModelForm
from django import forms
from django.utils.translation import ugettext, ugettext_lazy as _

from apps.accounts.models import User
from apps.profile.models import AssociateAccountProfile, StoreAccountProfile

class AssociateUserUpdateForm(ModelForm):

    """
    Update associates data updates
    """

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(AssociateUserUpdateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = User
        exclude = ['id','password','date_joined']

    def clean_username(self):
        # Check that the two password entries match
        username = self.cleaned_data.get("username").strip()
        if not username:
            raise forms.ValidationError("User Name already exist")
        return username
    def clean_email(self):
        # Check that the two password entries match
        email = self.cleaned_data.get("email")
        if not email:
            raise forms.ValidationError("This field is required.")
        try:
            user = User.objects.filter(email=email).exclude(email=self.request.email)
        except User.DoesNotExist:
            user = None
        if user:
            raise forms.ValidationError("Email with this user already exists.")
        return email

    def save(self, request, commit=True):
        user = super(AssociateUserUpdateForm, self).save(commit=False)
        if commit:
            user.is_active = True
            user.save()
        return user


class AssociateSettingsUpdateForm(ModelForm):

    """
    Update associates settings data updates
    """

    def __init__(self, *args, **kwargs):
        super(AssociateSettingsUpdateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = AssociateAccountProfile
        fields = ['designation','phone','address']
        exclude = ['user','associate_photo']

    def save(self, request, commit=True):
        user = super(AssociateSettingsUpdateForm, self).save(commit=False)
        if commit:
            user.save()
        return user


class AssociatePhotoUpdateForm(ModelForm):

    """
    Update associates settings data updates
    """

    def __init__(self, *args, **kwargs):
        super(AssociatePhotoUpdateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = AssociateAccountProfile
        fields = ['associate_photo']


class StoreProfileForm(ModelForm):
    """
    store profile form
    """
    def __init__(self, *args, **kwargs):
        super(StoreProfileForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-first-name form-control'
            self.fields['store_address'].widget.attrs['rows'] = '4'

    class Meta:
        model = StoreAccountProfile
        fields = ['store_name', 'jew_id', 'lear_lab_ID', 'store_address', 'city', 'state', 'zip_code', 'country', 'phone', 'website']


class StoreProfileUpdateForm(ModelForm):

    """
    Update store profile
    """
    def __init__(self, *args, **kwargs):
        super(StoreProfileUpdateForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
        self.fields['store_address'].widget.attrs['rows'] = '4'

    class Meta:
        model = StoreAccountProfile
        exclude = ['user']


class StoreAccountDetailsForm(ModelForm):
    """
    store account details form
    """
    def __init__(self, *args, **kwargs):
        super(StoreAccountDetailsForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-first-name form-control'
            self.fields['username'].widget.attrs['readonly'] = True

    class Meta:
        model = User
        fields =['first_name','last_name','username','email']



class StoreUserUpdateForm(ModelForm):

    """
    Update store user account
    """

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('request')
        super(StoreUserUpdateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = User
        fields =['first_name','last_name','username','email']

    def clean_username(self):
        # Check that the two password entries match
        username = self.cleaned_data.get("username").strip()
        if not username:
            raise forms.ValidationError("User Name already exist")
        return username
    def clean_email(self):
        # Check that the two password entries match
        email = self.cleaned_data.get("email")
        if not email:
            raise forms.ValidationError("This field is required.")
        try:
            user = User.objects.filter(email=email).exclude(email=self.user.email)
        except User.DoesNotExist:
            user = None
        if user:
            raise forms.ValidationError("Email with this user already exists.")
        return email


class StorePhotoUpdateForm(ModelForm):

    """
    Update associates settings data updates
    """

    def __init__(self, *args, **kwargs):
        super(StorePhotoUpdateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = StoreAccountProfile
        fields = ['store_pic']