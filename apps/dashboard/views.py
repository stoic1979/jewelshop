import json
import datetime


from django.views.generic.base import TemplateView, View
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth.forms import SetPasswordForm
from django.shortcuts import redirect,render
from pure_pagination.mixins import PaginationMixin

from apps.profile.models import StoreAssociateAccount
from apps.accounts.models import User
from apps.profile.models import AssociateAccountProfile, AdminStoreAccount, StoreAccountProfile
from .forms import AssociateUserUpdateForm, AssociateSettingsUpdateForm, AssociatePhotoUpdateForm, \
    StoreProfileUpdateForm, StoreProfileForm, StoreAccountDetailsForm, StoreUserUpdateForm, StorePhotoUpdateForm
from apps.leadquote.models import CustomerDetails, CustomerPremiumDetail
from apps.dashboard.mixins import DashBoardMixin

today = datetime.datetime.now()
current_year = today.year


class AssociateWiseLeadsView(DashBoardMixin, TemplateView):
    template_name = "associate_wise_leads.html"

    @csrf_exempt
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(AssociateWiseLeadsView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(AssociateWiseLeadsView, self).get_context_data(**kwargs)
        start_date, end_date, store, associates = self.request.GET.get('start_date'), self.request.GET.get('end_date'), \
                                      self.request.GET.get('store'), self.request.GET.getlist('associates')
        associate_list, grand_total = self.get_associates(start_date, end_date, store, associates)
        context['associate_list'] = associate_list
        context['grand_total'] = grand_total
        context['stores'] = StoreAccountProfile.objects.all()
        if store or self.request.user.groups.filter(name='store admin').exists():
            if store:
                store = store
            else:
                store = StoreAccountProfile.objects.get(user = self.request.user).id
            associate_profile_id = self.get_store_associates(store)
            context['get_associates'] = User.objects.filter(id__in=associate_profile_id)
        associates_list = []
        for associates_id in associates:
            associates_list.append(int(associates_id))
        context['associates_list'] = associates_list
        return context


class StoreWiseLeadsView(DashBoardMixin, TemplateView):
    template_name = "store_wise_leads.html"

    @csrf_exempt
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(StoreWiseLeadsView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(StoreWiseLeadsView, self).get_context_data(**kwargs)
        start_date, end_date, store = self.request.GET.get('start_date'), self.request.GET.get('end_date'), \
                                      self.request.GET.getlist('store')
        context['store_vise_list'] = self.get_store_wise_leads(start_date, end_date, store)
        context['stores'] = StoreAccountProfile.objects.all()
        store_list = []
        for store_id in store:
            store_list.append(int(store_id))
        context['selected_stores_list'] = store_list
        return context


class DashboardView(DashBoardMixin, TemplateView):
    template_name = "dashboard.html"

    @csrf_exempt
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DashboardView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        """

        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        context = self.get_context_data(**kwargs)
        chart = self.request.GET.get('chart')
        if chart:
            return HttpResponse(json.dumps(self.get_chart_dict_data()), content_type="application/json")
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        context['store_vise_list'] = self.get_store_wise_leads()
        context['associate_wise_list'] = self.get_associate_wise_leads()
        context['recent_leads'] = self.get_recent_leads()
        context['leads_count'] = self.get_leads_count()
        context['store_count'] = self.get_store_count()
        context['total_attainment'] = self.get_total_attainment()
        context['years'] = range(current_year-1, current_year+1, 1)
        return context

    def post(self, request, *args, **kwargs):
        """
        update request associate_account

        """
        response_data = {}
        response_data['status'] = True
        if request.is_ajax():
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            year = request.POST.get('year')
            if start_date and end_date:
                if request.POST.get('filterType') == 'associate_wise':
                    associate_wise_list = self.get_associate_wise_leads(start_date, end_date)
                    response_data['html_content'] = render_to_string('ajax/associate_wise_content.html',
                                                                     {'associate_wise_list': associate_wise_list})
                elif request.POST.get('filterType') == 'recent_leads':
                    recent_leads = self.get_recent_leads(start_date, end_date)
                    response_data['html_content'] = render_to_string('ajax/recent_leads_content.html',
                                                                     {'recent_leads': recent_leads})
                else:
                    store_vise_list = self.get_store_wise_leads(start_date, end_date)
                    response_data['html_content'] = render_to_string('ajax/store_wise_content.html',
                                                                     {'store_vise_list': store_vise_list,
                                                                      'total_attainment': self.get_total_attainment()})

            elif year:
                filtertype = request.POST.get('filterType')
                if filtertype == 'total_leads':
                    pending_count, success_count = self.get_barchart_data(year=year)
                    response_data.update({'pending_data': pending_count, 'success_data': success_count,
                                          'filtertype': filtertype})
                elif filtertype == 'revenue_chart':
                    month_names, revenue = self.get_revenue_data(year=year)
                    response_data.update({'months': month_names, 'revenue': revenue, 'filtertype': filtertype})
            return HttpResponse(json.dumps(response_data), content_type="application/json")


class AssociatesListFrontView(TemplateView):
    template_name = "associate_list.html"

    @csrf_exempt
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(AssociatesListFrontView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(AssociatesListFrontView, self).get_context_data(**kwargs)
        store_linked_ids = StoreAssociateAccount.objects.filter(store_account=self.request.user).values_list('user',
                                                                                                             flat=True)
        associates = User.objects.filter(id__in=store_linked_ids)
        context['associates'] = associates
        return context


class AssociatesListView(TemplateView):
    template_name = "associate_view.html"

    @csrf_exempt
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(AssociatesListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(AssociatesListView, self).get_context_data(**kwargs)
        stores = StoreAssociateAccount.objects.filter(store_account=self.request.user)
        store_linked_ids = stores.values_list('user', flat=True)
        associates = User.objects.filter(id__in=store_linked_ids)
        context['associates'] = associates

        return context


class AssociatesProfileView(TemplateView):
    template_name = "associate_profile.html"

    @csrf_exempt
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(AssociatesProfileView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(AssociatesProfileView, self).get_context_data(**kwargs)
        associate_slug = kwargs.get('slug')
        if associate_slug:
            try:
                associate = User.objects.get(name_slug_field=associate_slug)
            except User.DoesNotExist:
                associate = None
            context['associate'] = associate
        return context


class AssociatesProfileUpdate(View):
    @csrf_exempt
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(AssociatesProfileUpdate, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        update in associate profile

        """
        response_data = {}
        response_data['status'] = True
        if request.is_ajax():
            user_id = request.POST.get('user_id')
            user = User.objects.get(id=user_id)
            is_store_exists = user.groups.filter(name='store admin').exists()
            if is_store_exists:
                try:
                    if request.FILES:

                        store_profile = StoreAccountProfile.objects.get(user=user)
                        store_pic_form = StorePhotoUpdateForm(request.POST, request.FILES,
                                                                              instance=store_profile)
                        if store_pic_form.is_valid():
                            store_pic_form.save()
                        else:
                            response_data['status'] = False
                            response_data['errors'] = store_pic_form.errors
                    if request.POST.get('profile'):
                        form = AssociateUserUpdateForm(request.POST, request=user,  instance=user)
                        if form.is_valid():
                            form.save(request, commit=True)
                        else:
                            response_data['status'] = False
                            response_data['errors'] = form.errors
                except User.DoesNotExist:
                    response_data['status'] = False
                try:
                    associate = User.objects.get(id=user_id)
                    response_data['html_content'] = render_to_string('ajax/associate_settings_edit.html',
                                                                     {'associate': associate,})
                except User.DoesNotExist:
                    response_data['status'] = False

            else:
                try:
                    associate = User.objects.get(id=user_id)
                    if request.FILES:
                        associate_profile = AssociateAccountProfile.objects.get(user=associate)
                        associate_profile_form = AssociatePhotoUpdateForm(request.POST, request.FILES,
                                                                          instance=associate_profile)
                        if associate_profile_form.is_valid():
                            associate_profile_form.save()
                        else:
                            response_data['status'] = False
                            response_data['errors'] = associate_profile_form.errors
                    if request.POST.get('profile'):
                        form = AssociateUserUpdateForm(request.POST, request=associate,  instance=associate)
                        if form.is_valid():
                            form.save(request, commit=True)
                        else:
                            response_data['status'] = False
                            response_data['errors'] = form.errors
                except User.DoesNotExist:
                    response_data['status'] = False
                try:
                    associate = User.objects.get(id=user_id)
                    response_data['html_content'] = render_to_string('ajax/associate_settings_edit.html',
                                                                     {'associate': associate})
                except User.DoesNotExist:
                    response_data['status'] = False
            return HttpResponse(json.dumps(response_data), content_type="application/json")


class AssociatesProfileSettingsUpdate(View):
    @csrf_exempt
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(AssociatesProfileSettingsUpdate, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        update request associate_account

        """
        response_data = {}
        response_data['status'] = True
        if request.is_ajax():
            user_id = request.POST.get('user_id')
            try:
                user = User.objects.get(id=user_id)
                try:
                    associate = AssociateAccountProfile.objects.get(user=user)
                    form = AssociateSettingsUpdateForm(request.POST, instance=associate)
                    if form.is_valid():
                        form.save(request, commit=True)
                    else:
                        response_data['status'] = False
                        response_data['errors'] = form.errors
                except AssociateAccountProfile.DoesNotExist:
                    response_data['status'] = False
            except User.DoesNotExist:
                response_data['status'] = False
            return HttpResponse(json.dumps(response_data), content_type="application/json")


class AssociatesProfileData(View):
    @csrf_exempt
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(AssociatesProfileData, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        request associate profile

        """
        response_data = {}
        response_data['status'] = True
        associate_group = True
        if request.is_ajax():
            user_id = request.POST.get('user_id')
            try:
                associate = User.objects.get(id=user_id)
                if associate.groups.filter(name='super admin').exists():
                    associate_group = True
                else:
                    associate_group = False
                response_data['html_content'] = render_to_string('ajax/associate_profile_edit.html',
                                                                 {'associate': associate,
                                                                  'associate_group':associate_group,
                                                                  'user_type': 'store_admin'})
            except User.DoesNotExist:
                response_data['status'] = False
            return HttpResponse(json.dumps(response_data), content_type="application/json")

    def get(self, request, *args, **kwargs):
        """
        request associate account

        """
        response_data = {}
        response_data['status'] = True
        if request.is_ajax():
            user_id = request.GET.get('user_id')
            try:
                associate = User.objects.get(id=user_id)
                response_data['html_content'] = render_to_string('ajax/associate_settings_edit.html',
                                                                 {'associate': associate})
            except User.DoesNotExist:
                response_data['status'] = False
            return HttpResponse(json.dumps(response_data), content_type="application/json")


class StoreAccountListView(PaginationMixin, ListView):
    template_name = "store-list.html"
    paginate_by = 20

    @csrf_exempt
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(StoreAccountListView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        # queryset = super(StoreAccountListView, self).get_context_data(**kwargs)
        admins = AdminStoreAccount.objects.filter(super_admin_account=self.request.user)
        admin_linked_ids = admins.values_list('user', flat=True)
        store_holders = User.objects.filter(id__in=admin_linked_ids).order_by('-id')
        queryset = store_holders

        return queryset


class StoreProfileView(TemplateView):
    template_name = "store_profile.html"

    @csrf_exempt
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(StoreProfileView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(StoreProfileView, self).get_context_data(**kwargs)
        user_slug = kwargs.get('slug')
        context['user_form'] = {}
        if user_slug:
            try:
                user = User.objects.get(name_slug_field=user_slug)
                user_form = StoreAccountDetailsForm(instance=user)
                try:
                    store = StoreAccountProfile.objects.get(user=user)
                    store_form = StoreProfileForm(instance=store)
                except StoreAccountProfile.DoesNotExist:
                    store_form = None
                    user_form = None
            except User.DoesNotExist:
                user = None
                user_form = None
            context['user_account'] = user
            context['user_form'] = user_form
            context['store'] = store
            context['store_form'] = store_form
        return context


class StoreUpdateView(View):
    @csrf_exempt
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(StoreUpdateView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        update request store profile

        """
        response_data = {}
        response_data['status'] = True
        if request.is_ajax():
            user_id = request.POST.get('user_id')
            try:
                store = StoreAccountProfile.objects.get(id=user_id)
                form = StoreProfileUpdateForm(request.POST, request.FILES, instance=store)
                if form.is_valid():
                    form.save()
                else:
                    response_data['status'] = False
                    response_data['errors'] = form.errors
            except User.DoesNotExist:
                response_data['status'] = False
            try:
                store = StoreAccountProfile.objects.get(id=user_id)
                form = StoreProfileForm(instance=store)
                response_data['html_content'] = render_to_string('ajax/store_details_update.html',
                                                                 {'store': store, 'store_form': form})
            except StoreAccountProfile.DoesNoteExist:
                response_data['status'] = False
            return HttpResponse(json.dumps(response_data), content_type="application/json")


class StoreAccountUpdateView(View):
    @csrf_exempt
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(StoreAccountUpdateView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        update request store profile

        """
        response_data = {}
        response_data['status'] = True
        if request.is_ajax():
            user_id = request.POST.get('user_id')
            try:
                store_user = StoreAccountProfile.objects.get(id=user_id)
                user = User.objects.get(id=store_user.user.id)
                form = StoreUserUpdateForm(request.POST, request=user, instance=user)
                if form.is_valid():
                    form.save()
                else:
                    response_data['status'] = False
                    response_data['errors'] = form.errors
            except User.DoesNotExist:
                response_data['status'] = False
            try:
                store = StoreAccountProfile.objects.get(id=user_id)
                user = User.objects.get(id=store_user.user.id)
                form = StoreAccountDetailsForm(instance=user)
                response_data['html_content'] = render_to_string('ajax/store_account_user_update.html',
                                                                 {'user_account': user, 'user_form': form})
            except StoreAccountProfile.DoesNoteExist:
                response_data['status'] = False
            return HttpResponse(json.dumps(response_data), content_type="application/json")


class ChangePasswordView(View):
    @csrf_exempt
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ChangePasswordView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        request associate profile

        """
        response_data = {}
        response_data['status'] = True
        if request.is_ajax():
            user_id = request.POST.get('user_id')
            try:
                if request.POST.get('associate'):
                    user = User.objects.get(id=user_id)
                else:
                    store_user = StoreAccountProfile.objects.get(id=user_id)
                    user = User.objects.get(id=store_user.user.id)
                password = request.POST.get('password1')
                user.set_password(password)
                user.save()
            except User.DoesNotExist:
                response_data['status'] = False
            return HttpResponse(json.dumps(response_data), content_type="application/json")


class LeadQuotesProfileView(DetailView):
    template_name = "lead_quotes_profile.html"
    model = CustomerDetails
    slug_field = 'email_slug_field'
    slug_url_kwarg = 'email_slug_field'

    @csrf_exempt
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LeadQuotesProfileView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(LeadQuotesProfileView, self).get_context_data(**kwargs)
        customer = self.get_object()
        try:
            store_name = StoreAssociateAccount.objects.get(user=customer.user)
            store = StoreAccountProfile.objects.get(user=store_name.store_account)
            context['store'] = store
        except StoreAssociateAccount.DoesNotExist:
            context['store'] = {}
        return context


class StoreActiveStatus(PaginationMixin, ListView):
    paginate_by = 20

    @csrf_exempt
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(StoreActiveStatus, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        admins = AdminStoreAccount.objects.filter(super_admin_account=self.request.user)
        admin_linked_ids = admins.values_list('user', flat=True)
        queryset = User.objects.filter(id__in=admin_linked_ids).order_by('-id')
        return queryset

    def get(self, request, *args, **kwargs):
        """
        request associate profile

        """
        response_data = {}
        response_data['status'] = True
        if request.is_ajax():
            try:
                for checkbox in request.GET.getlist('checkbox[]'):
                    user = User.objects.get(id=checkbox)
                    user.is_active = False
                    user.save()
            except User.DoesNotExist:
                response_data['status'] = False
            store_holders = self.get_queryset()
            response_data['html_content'] = render_to_string('ajax/store_list_action.html',
                                                             {'store_holders': store_holders})
            return HttpResponse(json.dumps(response_data), content_type="application/json")

    def post(self, request, *args, **kwargs):
        """
        request associate profile

        """
        response_data = {}
        response_data['status'] = True
        if request.is_ajax():
            try:
                for checkbox in request.POST.getlist('checkbox[]'):
                    user = User.objects.get(id=checkbox)
                    user.is_active = True
                    user.save()
            except User.DoesNotExist:
                response_data['status'] = False
            store_holders = self.get_queryset()
            response_data['html_content'] = render_to_string('ajax/store_list_action.html',
                                                             {'store_holders': store_holders})
            return HttpResponse(json.dumps(response_data), content_type="application/json")


class StoreDeleteUsers(PaginationMixin, ListView):
    paginate_by = 20

    @csrf_exempt
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(StoreDeleteUsers, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        admins = AdminStoreAccount.objects.filter(super_admin_account=self.request.user)
        admin_linked_ids = admins.values_list('user', flat=True)
        queryset = User.objects.filter(id__in=admin_linked_ids).order_by('-id')
        return queryset

    def get(self, request, *args, **kwargs):
        """
        request associate profile

        """
        response_data = {}
        response_data['status'] = True
        dependent_status = False
        if request.is_ajax():
            try:
                for checkbox in request.GET.getlist('checkbox[]'):
                    user = User.objects.get(id=checkbox)
                    associate = StoreAssociateAccount.objects.filter(store_account=user).exists()
                    if associate == True:
                        dependent_status = True
                        response_data['dependent_status'] = True
                    else:
                        if dependent_status == True:
                            dependent_status = True
                        else:
                            dependent_status = False
                if dependent_status == False:
                    response_data['dependent_status'] = False
                    for checkbox in request.GET.getlist('checkbox[]'):
                        selected_user = User.objects.get(id=checkbox)
                        selected_user.delete()
                    store_holders = self.get_queryset()
                    response_data['html_content'] = render_to_string('ajax/store_list_action.html',
                                                                     {'store_holders': store_holders})
            except User.DoesNotExist:
                response_data['status'] = False
            return HttpResponse(json.dumps(response_data), content_type="application/json")

    def post(self, request, *args, **kwargs):
        """
        request associate profile

        """
        response_data = {}
        response_data['status'] = True
        if request.is_ajax():
            try:
                for checkbox in request.POST.getlist('checkbox[]'):
                    user = User.objects.get(id=checkbox)
                    associate = StoreAssociateAccount.objects.filter(store_account=user).exists()
                    if associate == True:
                        response_data['dependent_status'] = True
                    else:
                        user.delete()
            except User.DoesNotExist:
                response_data['status'] = False
            store_holders = self.get_queryset()
            response_data['html_content'] = render_to_string('ajax/store_list_action.html',
                                                             {'store_holders': store_holders})
            return HttpResponse(json.dumps(response_data), content_type="application/json")


class DeleteLeadAndQuote(View):
    @csrf_exempt
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DeleteLeadAndQuote, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        request associate profile

        """
        response_data = {}
        response_data['status'] = True
        if request.is_ajax():
            try:
                for checkbox in request.POST.getlist('checkbox[]'):
                    customer = CustomerDetails.objects.get(id=checkbox)
                    customer.delete()
            except CustomerDetails.DoesNotExist:
                response_data['status'] = False
            customers = self.get_queryset()
            response_data['html_content'] = render_to_string('ajax/leads_ajax_content.html',
                                                             {'customers':customers})
            return HttpResponse(json.dumps(response_data), content_type="application/json")

    def get_queryset(self):
        """
        Return the list of items for this view.

        The return value must be an iterable and may be an instance of
        `QuerySet` in which case `QuerySet` specific behavior will be enabled.
        """
        customer_ids = []
        is_user_exists = self.request.user.groups.filter(name='store admin').exists()
        if is_user_exists:
            store_associate_ids = StoreAssociateAccount.objects.filter(store_account=self.request.user). \
                values_list('user', flat=True)
            associates = User.objects.filter(id__in=store_associate_ids)
            for associate in associates:
                if associate.customer.all():
                    for customer in associate.customer.all():
                        customer_ids.append(customer.id)
            queryset = CustomerDetails.objects.filter(id__in=sorted(customer_ids))
        else:
            store_admins = User.objects.filter(groups__name='store admin')
            for store_admin in store_admins:
                associate_ids = store_admin.created_store.all().values_list('user', flat=True)
                associates = User.objects.filter(id__in=associate_ids)
                for associate in associates:
                    if associate.customer.all():
                        for customer in associate.customer.all():
                            customer_ids.append(customer.id)
            queryset = CustomerDetails.objects.filter(id__in=sorted(customer_ids))
        return queryset


class AdminProfileView(TemplateView):
    template_name = "admin_profile.html"

    @csrf_exempt
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(AdminProfileView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(AdminProfileView, self).get_context_data(**kwargs)
        user_slug = kwargs.get('slug')
        if user_slug:
            try:
                user = User.objects.get(name_slug_field=user_slug)
            except User.DoesNotExist:
                user = None

            try:
                is_user_exists = user.groups.filter(name='store admin').exists()
            except:
                is_user_exists = None
            if is_user_exists:
                store_ccount_profile = StoreAccountProfile.objects.get(user=user)
                store_ccount_profile_form = StoreProfileUpdateForm(instance=store_ccount_profile)
                context['form'] = store_ccount_profile_form
            context['user'] = user
        return context

    def post(self, request, *args, **kwargs):
        """
        request associate profile

        """
        response_data = {}
        response_data['status'] = True
        if request.is_ajax():
            store_slug = request.POST.get('store_slug')
            user = User.objects.get(name_slug_field=store_slug)
            store_ccount_profile = StoreAccountProfile.objects.get(user=user)
            form = StoreProfileUpdateForm(request.POST, instance=store_ccount_profile)
            if form.is_valid():
                form.save()
                response_data['html_content'] = render_to_string('ajax/store_edit_content.html',
                                                             {'user':user})
            else:
                response_data['status'] = False
                response_data['errors'] = form.errors
            return HttpResponse(json.dumps(response_data), content_type="application/json")


class AdminChangePasswordView(View):
    @csrf_exempt
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(AdminChangePasswordView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        request associate profile

        """
        response_data = {}
        response_data['status'] = True
        if request.is_ajax():
            user_id = request.POST.get('user_id')
            try:
                if request.POST.get('associate'):
                    user = User.objects.get(id=user_id)
                else:
                    store_user = StoreAccountProfile.objects.get(id=user_id)
                    user = User.objects.get(id=store_user.user.id)
                password_form = SetPasswordForm(user, request.POST)
                if password_form.is_valid():
                    password = password_form.cleaned_data.get('new_password1')
                    user.set_password(password)
                    user.save()
                else:
                    response_data['status'] = False
                    response_data['errors'] = password_form.errors
            except User.DoesNotExist:
                response_data['status'] = False
            return HttpResponse(json.dumps(response_data), content_type="application/json")


class UserDeleteView(View):
    model = User

    def get(self, request, *args, **kwargs):
        """
        request associate account

        """
        name_slug_field = kwargs.get('name_slug_field')
        try:
            user = User.objects.get(name_slug_field=name_slug_field)
            user.delete()
        except:
            pass
        return redirect('associates')


class LeadQuotesListView(PaginationMixin, ListView):
    template_name = "lead_quotes_listing.html"
    paginate_by = 15

    @csrf_exempt
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LeadQuotesListView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        """
        :return:
        """
        customer_ids = []
        is_user_exists = self.request.user.groups.filter(name='store admin').exists()
        if is_user_exists:
            store_associate_ids = StoreAssociateAccount.objects.filter(store_account=self.request.user). \
                values_list('user', flat=True)
            associates = User.objects.filter(id__in=store_associate_ids)
            for associate in associates:
                if associate.customer.all():
                    for customer in associate.customer.all():
                        customer_ids.append(customer.id)
            queryset = CustomerDetails.objects.filter(id__in=sorted(customer_ids))
        else:
            queryset = self.get_filter_data()

        return queryset

    def get_template_names(self):
        """
        Returns a list of template names to be used for the request. Must return
        a list. May not be called if render_to_response is overridden.
        """
        if self.template_name is None:
            raise ImproperlyConfigured(
                "TemplateResponseMixin requires either a definition of "
                "'template_name' or an implementation of 'get_template_names()'")
        elif self.request.user.groups.filter(name='super admin').exists():
            return 'lead_quotes_admin_listing.html'
        else:
            return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super(LeadQuotesListView, self).get_context_data(**kwargs)
        try:
            context['Stores'] = StoreAccountProfile.objects.all()
            context['start_date'] = self.request.GET.get('start_date')
            context['end_date'] = self.request.GET.get('end_date')
            store_id = self.request.GET.get('store')
            store = StoreAccountProfile.objects.get(pk=store_id)
            context['store'] = store
            associate_list = StoreAssociateAccount.objects.filter(store_account=store.user)
            context['associate_list'] = associate_list
            associate_obj = self.request.GET.getlist('associates')
            selected_associates = User.objects.filter(id__in=associate_obj)
            context['selected_associates'] = selected_associates
        except:
            context['Stores'] = StoreAccountProfile.objects.all()
        return context

    def get_filter_data(self):
        customer_ids = []
        customer_list = []
        try:
            data = self.get_request_data()
            start_date = data['start_date']
            end_date = data['end_date']
            store_id = data['store_id']
            associate_obj = data['associate_obj']
            if start_date and end_date and store_id and associate_obj:
                selected_associates = User.objects.filter(id__in=associate_obj)
                associates = self.get_associates(store_id)
                customer_details = self.get_associate_customer_ids(selected_associates, associates)
                customer_premium = CustomerPremiumDetail.objects.filter(effectiveDate__range=[start_date, end_date])
                for customer in customer_details:
                    for cust_prr in customer_premium:
                        if customer == cust_prr.customer:
                            customer_list.append(customer.id)
                customer_details = CustomerDetails.objects.filter(id__in=sorted(customer_list))
            elif start_date and end_date and store_id:
                associates = self.get_associates(store_id)
                customer_details = self.get_customer_details(associates)
                customer_premium = CustomerPremiumDetail.objects.filter(effectiveDate__range=[start_date, end_date])
                for customer in customer_details:
                    for cust_prr in customer_premium:
                        if customer == cust_prr.customer:
                            customer_list.append(customer.id)
                customer_details = CustomerDetails.objects.filter(id__in=sorted(customer_list))
            elif store_id and associate_obj:
                selected_associates = User.objects.filter(id__in=associate_obj)
                store_associate_ids = self.get_store_associate_ids(store_id)
                associates = User.objects.filter(id__in=store_associate_ids)
                customer_details = self.get_associate_customer_ids(selected_associates, associates)
            elif store_id == '0':
                customer_details = self.get_store_admins_customer()
            elif store_id:
                store_associate_ids = self.get_store_associate_ids(store_id)
                associates = User.objects.filter(id__in=store_associate_ids)
                customer_details = self.get_customer_details(associates)
            else:
                customer_details = self.get_store_admins_customer()
        except:
            customer_details = self.get_store_admins_customer()

        return customer_details

    def get_customer_details(self, associates):
        customer_ids = []
        for associate in associates:
            if associate.customer.all():
                for customer in associate.customer.all():
                    customer_ids.append(customer.id)
        customer_details = CustomerDetails.objects.filter(id__in=sorted(customer_ids))
        return customer_details

    def get_store_associate_ids(self, store_id):
        store_name = StoreAccountProfile.objects.get(pk=store_id)
        store_associate_ids = StoreAssociateAccount.objects.filter(store_account=store_name.user). \
                values_list('user', flat=True)
        return store_associate_ids

    def get_associates(self, store_id):
        store_associate_ids = self.get_store_associate_ids(store_id)
        associates = User.objects.filter(id__in=store_associate_ids)
        return associates

    def get_request_data(self):
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        store_id = self.request.GET.get('store')
        associate_obj = self.request.GET.getlist('associates')
        context ={'start_date': start_date, 'end_date': end_date, 'store_id': store_id, 'associate_obj' :associate_obj}
        return context

    def get_store_admins_customer(self):
        customer_ids = []
        store_admins = User.objects.filter(groups__name='store admin')
        for store_admin in store_admins:
            associate_ids = store_admin.created_store.all().values_list('user', flat=True)
            associates = User.objects.filter(id__in=associate_ids)
            for associate in associates:
                if associate.customer.all():
                    for customer in associate.customer.all():
                        customer_ids.append(customer.id)
        customer_details = CustomerDetails.objects.filter(id__in=sorted(customer_ids))
        return customer_details

    def get_associate_customer_ids(self, selected_associates, associates):
        customer_ids = []
        for select_associate in selected_associates:
            for associate in associates:
                if select_associate.id == associate.id:
                    if associate.customer.all():
                        for customer in associate.customer.all():
                            customer_ids.append(customer.id)
        customer_details = CustomerDetails.objects.filter(id__in=sorted(customer_ids))
        return customer_details


class LeadListView(TemplateView):
    template_name = "lead_quotes_listing.html"
    paginate_by = 10

    @csrf_exempt
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LeadListView, self).dispatch(*args, **kwargs)

    def get_template_names(self):
        """
        Returns a list of template names to be used for the request. Must return
        a list. May not be called if render_to_response is overridden.
        """
        if self.template_name is None:
            raise ImproperlyConfigured(
                "TemplateResponseMixin requires either a definition of "
                "'template_name' or an implementation of 'get_template_names()'")
        elif self.request.user.groups.filter(name='super admin').exists():
            return 'lead_quotes_admin_listing.html'
        else:
            return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super(LeadQuotesListView, self).get_context_data(**kwargs)
        context['Stores'] = StoreAccountProfile.objects.all()
        return context

    def get(self, request, *args, **kwargs):
        """
        get associate list
        """
        response_data = {}
        store = request.GET['store_id']
        filter_content = request.GET.get('filter_content')
        if store == '0':
            response_data['html_content'] = render_to_string('ajax/associate_empty.html')
        else:
            store_name = StoreAccountProfile.objects.get(pk=store)
            associate_list = StoreAssociateAccount.objects.filter(store_account=store_name.user)
            if filter_content == 'associate_wise':
                response_data['html_content'] = render_to_string('ajax/associate_content.html', {'associate_list': associate_list})
            else:
                response_data['html_content'] = render_to_string('ajax/associate_list.html', {'associate_list': associate_list})
        response_data['status'] = True
        return HttpResponse(json.dumps(response_data), content_type="application/json")

