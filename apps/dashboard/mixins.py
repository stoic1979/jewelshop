import datetime
import itertools
import json
from dateutil import relativedelta
from decimal import Decimal
from dateutil import parser

from apps.accounts.models import User
from apps.leadquote.models import CustomerDetails, CustomerPremiumDetail
from apps.profile.models import AssociateAccountProfile, AdminStoreAccount, StoreAccountProfile
from apps.profile.models import StoreAssociateAccount
from .forms import AssociateUserUpdateForm, AssociateSettingsUpdateForm, AssociatePhotoUpdateForm, \
    StoreProfileUpdateForm, StoreProfileForm, StoreAccountDetailsForm, StoreUserUpdateForm, StorePhotoUpdateForm

today = datetime.datetime.now()
current_year = today.year
current_month = today.month


class DashBoardMixin(object):
    def get_chart_dict_data(self):
        """

        :return:
        """
        response_data = {}
        pending_count, success_count = self.get_barchart_data()
        month_names, revenue = self.get_revenue_data()
        pending, success = self.get_total_pending_success_quote()
        response_data.update({'pending_data': pending_count, 'success_data': success_count, 'months': month_names,
                              'revenue': revenue, 'pending_count': pending, 'success_count': success})
        return response_data

    def get_total_pending_success_quote(self):
        """

        :return:
        """
        quote_list = []
        pending = 0
        success = 0
        if self.request.user.groups.filter(name='store admin').exists():
            for customer in self.get_customers(self.request.user):
                quote_list.append(CustomerPremiumDetail.objects.filter(customer=customer))
            quotes = list(itertools.chain(*quote_list))
            for quote in quotes:
                if quote.status == 'Pending':
                    pending += 1
                else:
                    success += 1
        else:
            quotes = CustomerPremiumDetail.objects.all()
            pending = quotes.filter(status="Pending").count()
            success = quotes.filter(status="Success").count()
        return pending, success

    def get_customers(self, user):
        """

        :param user:
        :return:
        """
        customers = []
        store_linked_ids = StoreAssociateAccount.objects.filter(store_account=user).values_list('user',
                                                                                                flat=True)
        associates = User.objects.filter(id__in=store_linked_ids)
        for associate in associates:
            if associate.customer.all():
                customers.append(associate.customer.all())
        return list(itertools.chain(*customers))

    def get_revenue_data(self, year=None):
        """
        Method to get month names with revenue data to draw revenue chart.
        :return: month_names, revenue
        """

        revenue = []
        if year:
            year = int(year)
        else:
            year = current_year
        month_names = [datetime.date(year, i, 1).strftime('%B') for i in range(1, current_month + 1)]
        month_count = ["0" + str(datetime.date(year, i, 1).month)
                       if datetime.date(year, i, 1).month == 1
                       else str(datetime.date(year, i, 1).month)
                       for i in range(1, current_month + 1)]

        for i in month_count:
            total = 0
            quote_list = []
            if self.request.user.groups.filter(name='store admin').exists():
                for customer in self.get_customers(self.request.user):
                    if CustomerPremiumDetail.objects.filter(customer=customer, effectiveDate__year=year,
                                                            effectiveDate__month=i):
                        quote_list.append(CustomerPremiumDetail.objects.
                                          filter(customer=customer, effectiveDate__year=year,
                                                 effectiveDate__month=i))
                quotes = list(itertools.chain(*quote_list))
            else:
                quotes = CustomerPremiumDetail.objects.filter(effectiveDate__year=year, effectiveDate__month=i)
            if quotes:
                for quote in quotes:
                    total += int(Decimal(quote.jewel_price))
                revenue.append(total)
            else:
                revenue.append(0)
        return month_names, revenue

    def get_barchart_data(self, year=None):
        """
        Method to get both pending and success quote submission status to draw the bar chart.

        :return: pending_count, success_count
        """
        months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
        pending_count = []
        success_count = []
        if year:
            year = year
        else:
            year = current_year
        if self.request.user.groups.filter(name='store admin').exists():
            for month in months:
                pending_status = 0
                success_status = 0
                for customer in self.get_customers(self.request.user):
                    if CustomerPremiumDetail.objects.filter(customer=customer, effectiveDate__year=year,
                                                            effectiveDate__month=month):
                        pending_status += CustomerPremiumDetail.objects.filter(customer=customer, status='Pending',
                                                                               effectiveDate__year=year,
                                                                               effectiveDate__month=month).count()
                        success_status += CustomerPremiumDetail.objects.filter(customer=customer, status='Success',
                                                                               effectiveDate__year=year,
                                                                               effectiveDate__month=month).count()
                pending_count.append(pending_status)
                success_count.append(success_status)
        else:
            pending_count = [CustomerPremiumDetail.objects.filter(effectiveDate__year=year,
                                                                  effectiveDate__month=month,
                                                                  status="Pending").count() for month in months]
            success_count = [CustomerPremiumDetail.objects.filter(effectiveDate__year=year,
                                                                  effectiveDate__month=month,
                                                                  status="Success").count() for month in months]
        return pending_count, success_count

    def get_leads_count(self):
        """

        :return: Quote count
        """
        count = 0
        if self.request.user.groups.filter(name='store admin').exists():
            for customer in self.get_customers(self.request.user):
                count += CustomerPremiumDetail.objects.filter(customer=customer).count()
        else:
            count = CustomerPremiumDetail.objects.all().count()
        return count

    def get_store_count(self):
        """

        :return: Store count
        """
        count = StoreAccountProfile.objects.all().count()
        return count

    def get_total_attainment(self):
        """

        :return:
        """
        total = 0
        quote_list = []
        if self.request.user.groups.filter(name='store admin').exists():
            for customer in self.get_customers(self.request.user):
                quote_list.append(CustomerPremiumDetail.objects.filter(customer=customer))
            for quote in list(itertools.chain(*quote_list)):
                total += int(Decimal(quote.jewel_price))
        else:
            for quote in CustomerPremiumDetail.objects.all():
                total += int(Decimal(quote.jewel_price))
        return total

    def get_total_quote_amount(self):
        """

        :return:
        """
        total = 0
        for quote in CustomerPremiumDetail.objects.all():
            total += int(Decimal(quote.jewel_price))
        return total

    def get_store_wise_leads(self, start_date=None, end_date=None, store=None):
        """

        :return:
        """
        associate_ids = []
        store_vise_list = []
        customers = []
        dics = {}
        if store:
            store_ids = [int(i) for i in store]
            store_profile_id = StoreAccountProfile.objects.filter(id__in=store_ids).values_list('user', flat=True)
        else:
            store_profile_id = StoreAccountProfile.objects.all().values_list('user', flat=True)
        store_holders = User.objects.filter(id__in=store_profile_id)
        for store in store_holders:
            associate_id = store.created_store.all().values_list('user', flat=True)
            total_jewel_price = 0
            if associate_id:
                associate_ids.append(associate_id)
                for pk in list(itertools.chain(*associate_ids)):
                    user = User.objects.get(pk=pk)
                    for customer in user.customer.all():
                        if customer.id not in customers:
                            if start_date and end_date:
                                quotes = CustomerPremiumDetail.objects. \
                                    filter(effectiveDate__range=[parser.parse(start_date), parser.parse(end_date)], customer=customer)
                            else:
                                quotes = customer.JewelryItems.all()
                            for quote in quotes:
                                price = quote.jewel_price
                                total_jewel_price += int(Decimal(price))
                                store_vise_dict = {'store': store, 'total': total_jewel_price}
                                if dics.get(store):
                                    dics[store].update({'total': total_jewel_price})
                                else:
                                    dics = {store: store_vise_dict}
                                if dics[store] not in store_vise_list:
                                    store_vise_list.append(dics[store])
                            if customer.id not in customers:
                                customers.append(customer.id)
        return sorted(store_vise_list, key=lambda k: k['total'], reverse=True)

    def get_recent_leads(self, start_date=None, end_date=None):
        """

        :return:
        """
        associate_ids = []
        recent_leads = []
        customers = []
        dics = {}
        if self.request.user.groups.filter(name='store admin').exists():
            store_profile_id = StoreAccountProfile.objects.filter(user=self.request.user).values_list('user', flat=True)
        else:
            store_profile_id = StoreAccountProfile.objects.all().values_list('user', flat=True)
        store_holders = User.objects.filter(id__in=store_profile_id)
        for store in store_holders:
            associate_id = store.created_store.all().values_list('user', flat=True)
            total_jewel_price = 0
            if associate_id:
                associate_ids.append(associate_id)
                for pk in list(itertools.chain(*associate_ids)):
                    user = User.objects.get(pk=pk)
                    for customer in user.customer.all():
                        if customer.id not in customers:
                            if start_date and end_date:
                                quotes = CustomerPremiumDetail.objects. \
                                    filter(effectiveDate__range=[parser.parse(start_date), parser.parse(end_date)], customer=customer).order_by(
                                    'id')
                            else:
                                quotes = customer.JewelryItems.all().order_by('id')
                            for quote in quotes:
                                price = quote.jewel_price
                                premium = quote.totalJewelryValue
                                store_vise_dict = {'customer': customer, 'store': store,
                                                   'price': price, 'quote': quote, 'premium': premium}
                                if store_vise_dict not in recent_leads:
                                    recent_leads.append(store_vise_dict)
                            if customer.id not in customers:
                                customers.append(customer.id)

        quotes = [x for x in recent_leads]
        return quotes

    def get_associate_wise_leads(self, start_date=None, end_date=None):
        """

        :return:
        """
        associate_ids = []
        associate_wise_list = []
        customers = []
        dics = {}
        if self.request.user.groups.filter(name='store admin').exists():
            associate_profile_id = StoreAssociateAccount.objects.filter(store_account=self.request.user).values_list(
                'user', flat=True)
        else:
            associate_profile_id = AssociateAccountProfile.objects.all().values_list('user', flat=True)
        associates = User.objects.filter(id__in=associate_profile_id)
        for associate in associates:
            associate_id = associate.associate_acc.all().values_list('user', flat=True)
            total_jewel_price = 0
            if associate_id:
                associate_ids.append(associate_id)
                for pk in list(itertools.chain(*associate_ids)):
                    user = User.objects.get(pk=pk)
                    store_associate_acc = StoreAssociateAccount.objects.get(user=user)
                    for customer in user.customer.all():
                        if customer.id not in customers:
                            if start_date and end_date:
                                quotes = CustomerPremiumDetail.objects. \
                                    filter(effectiveDate__range=[parser.parse(start_date), parser.parse(end_date)], customer=customer)
                            else:
                                quotes = customer.JewelryItems.all()
                            for quote in quotes:
                                price = quote.jewel_price
                                total_jewel_price += int(Decimal(price))
                                store_vise_dict = {'associate': associate, 'total': total_jewel_price,
                                                   'quote': quote, 'store_associate_acc': store_associate_acc}
                                if dics.get(associate):
                                    dics[associate].update({'total': total_jewel_price,
                                                            'quote': quote, 'store_associate_acc': store_associate_acc})
                                else:
                                    dics = {associate: store_vise_dict}
                                if dics[associate] not in associate_wise_list:
                                    associate_wise_list.append(dics[associate])
                            if customer.id not in customers:
                                customers.append(customer.id)
        quotes = [x for x in reversed(associate_wise_list)]
        return quotes

    def get_associates(self, start_date=None, end_date=None, store=None, associates=None):
        """
        :param start_date:
        :param end_date:
        :param store:
        :param associates:
        :return:associate_list, grand_total
        """
        dics = {}
        associate_ids = []
        associate_list = []
        if self.request.user.groups.filter(name='store admin').exists():
            associate_profile_id = StoreAssociateAccount.objects.filter(store_account=self.request.user). \
                values_list('user', flat=True)
        else:
            if store and associates:
                associate_profile_id = [int(i) for i in associates]
            elif store:
                associate_profile_id = self.get_store_associates(store)
            else:
                associate_profile_id = AssociateAccountProfile.objects.all().values_list('user', flat=True)
        associate_profile = User.objects.filter(id__in=associate_profile_id)
        for associate in associate_profile:
            associate_id = associate.associate_acc.all().values_list('user', flat=True)
            if associate_id:
                associate_ids.append(associate_id)
        associates = User.objects.filter(id__in=list(itertools.chain(*associate_ids)))
        grand_total = 0
        for asso in associates:
            total_jewel_price = 0
            total_jewel_value = 0
            quotes = []
            customer_list = []
            if asso.customer.all():
                for customer in asso.customer.all():
                    quote_count = 0
                    jewelery_type_total = 0
                    if start_date and end_date:
                        quote = CustomerPremiumDetail.objects.filter(customer=customer,
                                                                     effectiveDate__range=[parser.parse(start_date), parser.parse(end_date)], )
                    else:
                        quote = CustomerPremiumDetail.objects.filter(customer=customer)
                    if quote:
                        for q in quote:
                            total_customer_jewel_price = 0
                            jewel_price = q.jewel_price
                            totalJewelryValue = q.totalJewelryValue
                            if jewel_price:
                                total_jewel_price += int(Decimal(jewel_price))
                                total_customer_jewel_price += int(Decimal(jewel_price))
                                total_jewel_value += int(Decimal(jewel_price))
                                grand_total += int(Decimal(jewel_price))
                                jewelery_type_total += int(Decimal(jewel_price))
                            if totalJewelryValue:
                                pass
                            quote_count += 1
                            if quote_count > 1:
                                total_customer_jewel_price = jewelery_type_total
                            quote_submission_date = q.effectiveDate
                        quotes.append(quote)
                        customer_dict = {'customer': customer, 'quote_count': quote_count,
                                         'quote_submission_date': quote_submission_date,
                                         'total_customer_jewel_price': total_customer_jewel_price}
                        if dics.get(customer):
                            dics[customer].update({'quote_count': quote_count,
                                                   'quote_submission_date': quote_submission_date,
                                                   'total_customer_jewel_price': total_customer_jewel_price})
                        else:
                            dics = {customer: customer_dict}
                        if dics[customer] not in customer_list:
                            customer_list.append(dics[customer])
            if quotes:
                associate_dict = {'associate': asso, 'quote': list(itertools.chain(*quotes)),
                                  'jewel_count': len(list(itertools.chain(*quotes))),
                                  'total_jewel_price': total_jewel_price,
                                  'total_jewel_value': total_jewel_value,
                                  'customer_list': customer_list}
                associate_list.append(associate_dict)
        return associate_list, grand_total

    def get_store_associates(self, pk):
        """

        :param pk: store account
        :return: store linked associates.
        """
        try:
            store = StoreAccountProfile.objects.get(pk=int(pk))
        except:
            store = None
        associate_profile_id = StoreAssociateAccount.objects.filter(store_account=store.user). \
            values_list('user', flat=True)
        return associate_profile_id
