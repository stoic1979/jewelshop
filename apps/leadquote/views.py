import json
from django.views.generic.edit import FormView
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.utils.encoding import force_text
from django.core.exceptions import ImproperlyConfigured
from django.forms import modelformset_factory
from django.views.generic.base import TemplateView, View
from django.shortcuts import render_to_response
from django.shortcuts import render
from django.template.defaultfilters import slugify
from apps.general.utils import send_email
from django.contrib.sites.models import Site
from apps.leadquote.forms import CustomerDetailsForm, JewelleryDetailsForm, JewelleryDetailsFormSet
from apps.leadquote.mixins import LeadQuoteMixin
from apps.accounts.models import User
from apps.leadquote.models import JewelleryDetails, CustomerDetails, CustomerPremiumDetail, JewelleryType


class CustomerView(LeadQuoteMixin, FormView):
    template_name = 'customer_form.html'
    form_class = CustomerDetailsForm
    success_url = '/thanks/'

    @csrf_exempt
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CustomerView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = {}
        response_data = {}
        response_data['error_status'] = True
        if request.method == 'GET' and request.is_ajax():
            is_valid_postal_code = False
            error = ''
            zip_code = request.GET.get('zip_code').encode('utf8')
            if zip_code.isdigit():
                is_valid_postal_code, error = self.is_valid_postal_code(zip_code)
            else:
                context['zip_code_type_error_message'] = 'Please enter a valid zip code.'
                response_data['error_status'] = False

            if is_valid_postal_code:
                zip_country_list = self.get_zipcode_countries(zip_code)
                context['zip_country_list'] = zip_country_list
                print "zip_country_list", type(zip_country_list)
            else:
                context['zip_code_error_message'] = error
                response_data['error_status'] = False
            response_data['html_content'] = render_to_string('ajax/country_list_render.html', {'context': context})
            response_data['status'] = False
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        return super(CustomerView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CustomerView, self).get_context_data(**kwargs)
        is_slug, user = self.get_slug()
        context['is_slug'] = is_slug
        context['associate'] = user
        return context

    def form_valid(self, form):
        associate = self.request.POST.get('associate_pk')
        country_select = form.cleaned_data['country_select']
        print "country_select country_select", type(country_select)
        if associate:
            associate = User.objects.get(pk=int(associate))
            customer = form.save(associate, country_select=country_select)
            return redirect('jewellery-type', slug=associate.name_slug_field, email_slug=customer.email_slug_field)
        return super(CustomerView, self).form_valid(form)

    def form_invalid(self, form):
        """
        If the form is invalid, re-render the context data with the
        data-filled form and errors.
        """
        print "cccccccccccc", form.errors.as_text()
        return self.render_to_response(self.get_context_data(form=form))

    def get_slug(self, **kwargs):
        slug = self.kwargs.get('slug')
        is_slug = False
        if slug:
            try:
                user = User.objects.get(name_slug_field=slug)
            except:
                pass
            is_slug = True
        return is_slug, user


class JewelleryTypeView(LeadQuoteMixin, TemplateView):
    template_name = 'jewellery_type.html'
    form_class = CustomerDetailsForm

    @csrf_exempt
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(JewelleryTypeView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(JewelleryTypeView, self).get_context_data(**kwargs)
        is_slug, user, is_customer_email_slug = self.get_slug()
        context.update({'is_slug': is_slug, 'associate': user, 'is_customer_email_slug': is_customer_email_slug})
        context['jewellerydetailsformSet'] = JewelleryDetailsFormSet()
        return context

    def post(self, request, *args, **kwargs):
        jewellerydetailsformSet = JewelleryDetailsFormSet(request.POST)
        context = self.get_context_data(**kwargs)
        if jewellerydetailsformSet.is_valid():
            customer_slug = self.request.POST.get('customer_slug')
            customer = CustomerDetails.objects.get(email_slug_field=customer_slug)
            instances = jewellerydetailsformSet.save(commit=False)
            for instance in instances:
                instance.customer = customer
                instance.save()
            premium_content = self.get_rating_json_content(jewellerydetailsformSet, customer)
            if premium_content:
                is_slug, user, is_customer_email_slug = self.get_slug()
                return redirect('premium_content', email_slug=customer.email_slug_field, slug=self.kwargs.get('slug'))
        else:
            print "vvvvvvvvvvvvvvv", jewellerydetailsformSet.errors
            jewellerydetailsformSet = JewelleryDetailsFormSet()
            context['jewellerydetailsformSet'] = jewellerydetailsformSet
        return render_to_response(self.template_name, context)

    def get_slug(self, **kwargs):
        slug = self.kwargs.get('slug')
        is_customer_email_slug = self.kwargs.get('email_slug')
        is_slug = False
        if slug:
            try:
                user = User.objects.get(name_slug_field=slug)
            except:
                pass
            is_slug = True
        return is_slug, user, is_customer_email_slug


class PremiumSelectView(LeadQuoteMixin, TemplateView):
    template_name = 'choosedeductible.html'

    @csrf_exempt
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(PremiumSelectView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PremiumSelectView, self).get_context_data(**kwargs)
        context['premium_content'] = self.get_premium_content()
        print "*************"
        # print "get_premium_content", self.get_premium_content()
        # data = self.get_premium_content()
        # print "******** ", data.get('effectiveDate')
        context['initial_total'] = self.get_initial_total_amt(self.get_premium_content())
        context['customer_email_slug'] = self.get_email_slug()
        context['customer_email'] = CustomerDetails.objects.get(email_slug_field=self.get_email_slug())
        is_slug, user = self.get_associate_slug()
        context['user'] = user
        return context

    def get(self, request, *args, **kwargs):
        context = {}
        response_data = {}
        if request.method == 'GET' and request.is_ajax():
            item_id = request.GET.get('item_id')
            deduction = request.GET.get('deduction')
            premium = request.GET.get('premium')
            taxesAndSurcharges = request.GET.get('taxesAndSurcharges')
            item_value = request.GET.get('item_value')
            item_name = request.GET.get('item_name')
            is_slug, user = self.get_associate_slug()
            context['user'] = user
            context.update({'item_id': item_id, 'deduction': deduction, 'taxesAndSurcharges': taxesAndSurcharges,
                            'premium': premium, 'item_value': item_value,
                            'item_name': item_name})
            response_data['html_content'] = render_to_string('ajax/premium_content.html', {'context': context})
            response_data['status'] = False
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        return super(PremiumSelectView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        response_data = {}
        is_slug, user = self.get_associate_slug()
        product_api_details = json.loads(request.POST['pdt_api_data'])
        if request.method == 'POST' and request.is_ajax():
            lead_data_list = request.POST.getlist('my_data')[0]

            def get_boolean(data):
                data_val = data.encode('ascii', 'ignore')
                if data_val == 'True':
                    boolean_val = True
                elif data_val == 'False':
                    boolean_val = False
                return boolean_val
            customer_email_slug = slugify(request.POST.get('customer_email_slug').encode('utf-8'))
            for lead_data_dict in json.loads(lead_data_list):
                itemId = lead_data_dict.get('itemId')
                try:
                    jewel_type = JewelleryType.objects.get(pk=int(itemId))
                    customer = CustomerDetails.objects.get(email_slug_field=customer_email_slug)
                except:
                    jewel_type = None
                customer_premium = CustomerPremiumDetail(selected_jewellery=jewel_type, premium=lead_data_dict.get('premium_amount'),
                                      deduction=lead_data_dict.get('deduction_amount'),
                                      jewel_price=lead_data_dict.get('jewel_price'),
                                      taxesAndSurcharges=lead_data_dict.get('taxesAndSurcharges'),
                                      customer=customer,
                                      effectiveDate= product_api_details.get('effectiveDate'),
                                      minTaxesAndSurcharges= product_api_details.get('minTaxesAndSurcharges'),
                                      accountLocation= product_api_details.get('accountLocation'),
                                      isJewelersMutualPolicyholder=get_boolean(product_api_details.get('isJewelersMutualPolicyholder')),
                                      totalJewelryValue= product_api_details.get('totalJewelryValue'),
                                      safeConcealed=get_boolean(product_api_details.get('safeConcealed')),
                                      safeAnchored=get_boolean(product_api_details.get('safeAnchored')),
                                      safeWeightClass= product_api_details.get('safeWeightClass'),
                                      alarmType= product_api_details.get('alarmType'),
                                      safeType= product_api_details.get('safeType'),
                                      isEmailAlreadyUsed= get_boolean(product_api_details.get('isEmailAlreadyUsed')),
                                      isJewelersMutualCareTips= get_boolean(product_api_details.get('isJewelersMutualCareTips')),
                                      jewelerCode= product_api_details.get('jewelerCode'),
                                      isPlatinumPoints=get_boolean(product_api_details.get('isPlatinumPoints')),
                                      emailAddress= product_api_details.get('emailAddress'),
                                      minPremium= product_api_details.get('minPremium'),
                                      notificationEmail= product_api_details.get('notification_email'),
                                      IsNotificationEmailSend=get_boolean(product_api_details.get('notification_send')),
                                      )
                customer_premium.save()
                response_data['trans_id'] = customer.transaction_id
            return HttpResponse(json.dumps(response_data), content_type="application/json")

        return render_to_response(self.template_name, context)

    def get_email_slug(self, **kwargs):
        customer_email_slug = self.kwargs.get('email_slug')
        return customer_email_slug

    def get_associate_slug(self, **kwargs):
        slug = self.kwargs.get('slug')
        is_slug = False
        if slug:
            try:
                user = User.objects.get(name_slug_field=slug)
            except:
                pass
            is_slug = True
        return is_slug, user


class EmailSendView(View):


    @csrf_exempt
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(EmailSendView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        response_data = {}
        response_data['status'] = True
        if request.is_ajax:
            user_id = request.POST.get('user_id')
            user = CustomerDetails.objects.get(id=user_id)
            email = request.POST.get('email')
            send_email(template_name='emails/jewelers-mutual.html', to_email=[email], context={'user': user,
                                                                                                'site': Site.objects.get_current()})

            return HttpResponse(json.dumps(response_data), content_type="application/json")