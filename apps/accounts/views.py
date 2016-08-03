import json
import random
import string
from django.views.generic.base import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.exceptions import ImproperlyConfigured
from apps.general.utils import send_email
from django.contrib.sites.models import Site

from django.contrib.auth.models import Group
from django.views.generic.edit import FormView, View
from django.http import HttpResponse
from apps.accounts.models import User

from django.views.generic.edit import UpdateView
from django.shortcuts import redirect
from django.conf import settings
from django.shortcuts import resolve_url
from django.template.response import TemplateResponse
from django.shortcuts import render, render_to_response
from django.template import RequestContext

from .forms import AccountCreationForm, StoreAccountProfileForm, AssociateAccountProfileForm, UserRoleForm
from apps.profile.models import StoreAssociateAccount, AdminStoreAccount


class SignUpView(TemplateView):
    form_class = AccountCreationForm
    store_acc_profile_form = StoreAccountProfileForm
    template_name = "registration/sign_up.html"

    @csrf_exempt
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SignUpView, self).dispatch(*args, **kwargs)

    def get_template_names(self):
        """
        Returns a list of template names to be used for the request. Must return
        a list. May not be called if render_to_response is overridden.
        """
        if self.template_name is None:
            raise ImproperlyConfigured(
                "TemplateResponseMixin requires either a definition of "
                "'template_name' or an implementation of 'get_template_names()'")
        elif self.request.user.groups.filter(name='store admin').exists():
            return 'registration/associate_sign_up.html'
        else:
            return [self.template_name]

    def get_context_data(self, **kwargs):
        acount_form = self.form_class()
        store_acc_profile_form = self.store_acc_profile_form()
        context = super(SignUpView, self).get_context_data(**kwargs)
        context['store_acount_form'] = acount_form
        context['store_acc_profile_form'] = store_acc_profile_form
        context['associate_acc_profile_form'] = AssociateAccountProfileForm()
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        """

        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        context = self.get_context_data(**kwargs)
        if request.POST.get('account_type') == 'sign-up':
            account_form = self.form_class(request.POST)
            store_acc_profile_form = self.store_acc_profile_form(request.POST, request.FILES)
            if account_form.is_valid() and store_acc_profile_form.is_valid:
                user = account_form.save()
                store_acc_profile_form.save(user, request.POST.get('account_type'))
                self.set_admin_to_store(user)
            else:
                print "store_acc_profile_form", store_acc_profile_form.errors.as_text()
                print "store_account_form", account_form.errors.as_text()
        elif request.POST.get('account_type') == 'associate_sign-up':
            associate_acc_profile_form = AssociateAccountProfileForm(request.POST, request.FILES)
            account_form = AccountCreationForm(request.POST)
            if account_form.is_valid() and associate_acc_profile_form.is_valid():
                user = account_form.save()
                associate_acc_profile_form.save(user, request.POST.get('account_type'))
                self.set_store_to_associate(user)
            else:
                print "associate_acc_profile_form", associate_acc_profile_form.errors.as_text()
                print "account_form account_form", account_form.errors.as_text()
        return self.render_to_response(context)

    def set_store_to_associate(self, user):
        """
        set store to associate
        :param user:
        :return: Boolean
        """
        p, created = StoreAssociateAccount.objects.get_or_create(user=user, store_account=self.request.user)
        if created:
            self.set_permission(user)
        return True

    def set_admin_to_store(self, user):
        """
        set store to associate
        :param user:
        :return: Boolean
        """
        p, created = AdminStoreAccount.objects.get_or_create(user=user, super_admin_account=self.request.user)
        if created:
            pass
            # self.set_store_permission(user)
        return True


    def set_permission(self, user):
        """

        :param user:
        :return:
        """
        group = Group.objects.get(name='associate admin')
        user.groups.add(group)

    def set_store_permission(self, user):
        """

        :param user:
        :return:
        """
        group = Group.objects.get(name='store admin')
        user.groups.add(group)


# class AssociateFieldCheckView(View):
#     model = User
#
#     @csrf_exempt
#     @method_decorator(login_required)
#     def dispatch(self, *args, **kwargs):
#         return super(AssociateFieldCheckView, self).dispatch(*args, **kwargs)
#
#     def post(self, request, *args, **kwargs):
#         """
#         ckecking entered emails is existing
#
#         """
#         print request.POST
#         response_data = {}
#         response_data['status'] = True
#         response_data['email_status'] = False
#         if request.is_ajax():
#             print "data:::", self.request.POST
#             email = self.request.POST.get('accociate_email')
#             try:
#                 user = User.objects.get(email=email)
#             except User.DoesNotExist:
#                 response_data['email_status'] = True
#             return HttpResponse(json.dumps(response_data), content_type="application/json")
#
#     def get(self, request, *args, **kwargs):
#         """
#         ckecking entered username is existing
#
#         """
#         print request.POST
#         response_data = {}
#         response_data['status'] = True
#         response_data['user_name_status'] = False
#         if request.is_ajax():
#             print "data:::", self.request.GET
#             user_name = self.request.GET.get('accociate_user_name')
#             try:
#                 user = User.objects.get(username=user_name)
#             except User.DoesNotExist:
#                 response_data['user_name_status'] = True
#             return HttpResponse(json.dumps(response_data), content_type="application/json")


class AssociateFieldCheckView(View):
    model = User
    form_class = AccountCreationForm
    store_acc_profile_form = StoreAccountProfileForm

    @csrf_exempt
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(AssociateFieldCheckView, self).dispatch(*args, **kwargs)
    #
    # def get(self, request, *args, **kwargs):
    #     """
    #     ckecking entered username is existing
    #
    #     """
    #     print request.POST
    #     response_data = {}
    #     response_data['status'] = True
    #     response_data['user_name_status'] = False
    #     if request.is_ajax():
    #         print "data:::", self.request.GET
    #         user_name = self.request.GET.get('accociate_user_name')
    #         try:
    #             user = User.objects.get(username=user_name)
    #         except User.DoesNotExist:
    #             response_data['user_name_status'] = True
    #         return HttpResponse(json.dumps(response_data), content_type="application/json")

    def post(self, request, *args, **kwargs):
        """
        ckecking entered emails is existing

        """
        acc_type = request.POST.get('acc_type')
        response_data = {}
        nexts = request.POST.get('next')
        if request.is_ajax() and acc_type == 'store':
            if nexts == 'next1':
                response_data['next'] = 'next1'
                account_form = self.form_class(request.POST)
                if account_form.is_valid():
                    response_data['acc_form_status'] = True
                else:
                    response_data['acc_form_status'] = False
                    print "account_form.errors", account_form.errors.as_text()
                    response_data['acc_form_errors'] = account_form.errors
            else:
                response_data['next'] = 'next2'
                store_profile_form = StoreAccountProfileForm(request.POST, request.FILES)
                if store_profile_form.is_valid():
                    response_data['store_profile_status'] = True
                else:
                    response_data['store_profile_status'] = False
                    print "account_form.errors", store_profile_form.errors.as_text()
                    response_data['store_profile_form_errors'] = store_profile_form.errors

        elif request.is_ajax() and acc_type == 'associate':
            print "associate section......................"
            if nexts == 'next1':
                response_data['next'] = 'next1'
                account_form = self.form_class(request.POST)
                if account_form.is_valid():
                    response_data['acc_form_status'] = True
                else:
                    response_data['acc_form_status'] = False
                    print "account_form.errors", account_form.errors.as_text()
                    response_data['acc_form_errors'] = account_form.errors

            else:
                print "associate section......................next2"
                response_data['next'] = 'next2'
                associate_acc_profile_form = AssociateAccountProfileForm(request.POST, request.FILES)
                if associate_acc_profile_form.is_valid():
                    response_data['associate_profile_status'] = True
                else:
                    response_data['associate_profile_status'] = False
                    print "associate_acc_profile_form.errors", associate_acc_profile_form.errors.as_text()
                    response_data['associate_profile_form_errors'] = associate_acc_profile_form.errors

        return HttpResponse(json.dumps(response_data), content_type="application/json")


class SetUserRoleView(FormView):
    template_name = 'user_role.html'
    form_class = UserRoleForm
    success_url = '/accounts/user-role-setting/'

    def form_valid(self, form):
        print "validddddddddddd"
        form.save()
        return super(SetUserRoleView, self).form_valid(form)


class ActivationView(TemplateView):
    template_name = "registration/activate_user.html"

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(ActivationView, self).dispatch(*args, **kwargs)


# class UserUpdateView(UpdateView):
#     model = User
#     form_class = UserEditForm
#     template_name = "user_update_form.html"
#     success_url = '/dashboard/'
#
#     @csrf_exempt
#     @method_decorator(login_required)
#     def dispatch(self, *args, **kwargs):
#         return super(UserUpdateView, self).dispatch(*args, **kwargs)

class ForgotPassword(View):

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(ForgotPassword, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
            send a new password if user is existing with the given mail
        """
        response_data = {}
        response_data['status'] = True
        if request.is_ajax:
            print"***********"
            print 'user_id', request.POST.get('email')
            email = request.POST.get('email')
            try:
                user = User.objects.get(email=email)
                email = request.POST.get('email')
                password = self.PasswordGenerate(email)
                print "password", password
                user.set_password(password)
                user.save()
                send_email(template_name='emails/password_send.html', to_email=[email],
                           context={'password': password, 'user': user,  'site': Site.objects.get_current()})
            except User.DoesNotExist:
                response_data['status'] = False
            return HttpResponse(json.dumps(response_data), content_type="application/json")


    def PasswordGenerate(self, email):
        N = 6
        new_password = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N))
        return new_password

