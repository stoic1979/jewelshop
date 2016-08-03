
from django import forms
from django.contrib.auth.models import Group


from apps.accounts.models import User
from apps.profile.models import StoreAccountProfile, AssociateAccountProfile
from .admin import UserCreationForm as BaseUserCreationForm


class AccountCreationForm(BaseUserCreationForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name'
                  )

    def clean_email(self):
        # Check that the two password entries match
        email = self.cleaned_data.get("email")
        if not email:
            raise forms.ValidationError("This field is required.")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = None
        if user:
            raise forms.ValidationError("Email with this user already exists.")
        return email

    def clean_first_name(self):
        # Check that the two password entries match
        first_name = self.cleaned_data.get("first_name").strip()
        if not first_name:
            raise forms.ValidationError("This field is required.")
        return first_name

    def clean_last_name(self):
        # Check that the two password entries match
        last_name = self.cleaned_data.get("last_name").strip()
        if not last_name:
            raise forms.ValidationError("This field is required.")
        return last_name

    def clean_username(self):
        # Check that the two password entries match
        username = self.cleaned_data.get("username").strip()
        if not username:
            raise forms.ValidationError("This field is required.")
        return username


class StoreAccountProfileForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(StoreAccountProfileForm, self).__init__(*args, **kwargs)
        # for field in self.fields:
        #     print field
        self.fields['country'].widget.attrs['class'] = 'form-first-name form-control'
        self.fields['country'].initial = 234

    class Meta:
        model = StoreAccountProfile
        fields = ['store_name', 'jew_id', 'lear_lab_ID', 'city', 'state',
                  'store_address', 'country', 'phone', 'website', 'store_pic']

    def save(self, user, account_type, commit=True, *args, **kwargs):
        store_acc_profile = super(StoreAccountProfileForm, self).save(commit=False)
        if commit:
            print " commit------------------"
            if account_type == 'associate_sign-up':
                g = Group.objects.get(name='associate admin')
                g.user_set.add(user)

            elif account_type == 'sign-up':
                g = Group.objects.get(name='store admin')
                g.user_set.add(user)
            store_acc_profile.user = user
            store_acc_profile.save()
        return store_acc_profile

    def clean_store_address(self):
        store_address = self.cleaned_data.get("store_address").strip()
        if not store_address:
            raise forms.ValidationError("This field is required.")
        return store_address

    def clean_store_name(self):
        store_name = self.cleaned_data.get("store_name").strip()
        if not store_name:
            raise forms.ValidationError("This field is required.")
        return store_name

    def clean_jew_id(self):
        jew_id = self.cleaned_data.get("jew_id").strip()
        if not jew_id:
            raise forms.ValidationError("This field is required.")
        return jew_id

    def clean_lear_lab_ID(self):
        lear_lab_ID = self.cleaned_data.get("lear_lab_ID").strip()
        if not lear_lab_ID:
            raise forms.ValidationError("This field is required.")
        return lear_lab_ID

    def clean_city(self):
        city = self.cleaned_data.get("city").strip()
        if not city:
            raise forms.ValidationError("This field is required.")
        return city

    def clean_state(self):
        state = self.cleaned_data.get("state").strip()
        if not state:
            raise forms.ValidationError("This field is required.")
        return state


    def clean_phone(self):
        phone = self.cleaned_data.get("phone").strip()
        if not phone:
            raise forms.ValidationError("This field is required.")
        return phone

    def clean_website(self):
        website = self.cleaned_data.get("website").strip()
        if not website:
            raise forms.ValidationError("This field is required.")
        return website


class AssociateAccountProfileForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(AssociateAccountProfileForm, self).__init__(*args, **kwargs)
        # for field in self.fields:
        #     print field
        #     self.fields[field].widget.attrs['class'] = 'loginfields'

    class Meta:
        model = AssociateAccountProfile
        fields = ['designation',
                  'address', 'associate_photo', 'phone', 'associate_code', ]

    def save(self, user, commit=True, *args, **kwargs):
        associate_acc_profile = super(AssociateAccountProfileForm, self).save(commit=False)
        if commit:
            print " commit------------------"
            associate_acc_profile.user = user
            associate_acc_profile.save()
        return associate_acc_profile

    def clean_address(self):
        address = self.cleaned_data.get("address").strip()
        if not address:
            raise forms.ValidationError("This field is required.")
        return address

    def clean_designation(self):
        designation = self.cleaned_data.get("designation").strip()
        if not designation:
            raise forms.ValidationError("This field is required.")
        return designation

    def clean_phone(self):
        phone = self.cleaned_data.get("phone").strip()
        if not phone:
            raise forms.ValidationError("This field is required.")
        return phone

    def clean_associate_code(self):
        associate_code = self.cleaned_data.get("associate_code").strip()
        if len(associate_code) < 6:
            raise forms.ValidationError("This field is required minimum 6 characters.")
        if not associate_code:
            raise forms.ValidationError("This field is required.")
        try:
            associate = AssociateAccountProfile.objects.get(associate_code=associate_code)
        except AssociateAccountProfile.DoesNotExist:
            associate = None
        if associate:
            raise forms.ValidationError("Associate code already exists.")
        return associate_code


class UserRoleForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(UserRoleForm, self).__init__(*args, **kwargs)

        self.fields['permissions'].widget.attrs['class'] = 'form-control'
        self.fields['permissions'].widget.attrs['id'] = 'roleSelection'
        self.fields['name'].widget.attrs['class'] = 'form-control'
        self.fields['name'].widget.attrs['placeholder'] = 'Name.....'

    class Meta:
        model = Group
        fields = ['name', 'permissions']



class UsernameEmailForm(forms.Form):
    email = forms.EmailField(label='Email address')
