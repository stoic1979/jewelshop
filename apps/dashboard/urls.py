from django.conf.urls import url

from apps.dashboard.views import AssociatesListFrontView, AssociatesListView, AssociatesProfileView, \
    AssociatesProfileUpdate, AssociatesProfileSettingsUpdate, AssociatesProfileData, StoreAccountListView, \
    StoreProfileView, StoreUpdateView, StoreAccountUpdateView, ChangePasswordView, LeadQuotesListView, \
    LeadQuotesProfileView, StoreActiveStatus, StoreDeleteUsers, DeleteLeadAndQuote, AdminProfileView,\
    AdminChangePasswordView, UserDeleteView, DashboardView, LeadListView, StoreWiseLeadsView, AssociateWiseLeadsView

urlpatterns = [
    url(r'^my-associates/$', AssociatesListFrontView.as_view(), name='associates'),
    url(r'^associate/$', AssociatesListView.as_view(), name='associate-view'),
    url(r'^associate-profile-update/$', AssociatesProfileUpdate.as_view(), name='associate_save_edit'),
    url(r'^associate-profile_settings-update/$', AssociatesProfileSettingsUpdate.as_view(),
        name='associate_settings_edit'),
    url(r'^associate-profile-data/$', AssociatesProfileData.as_view(), name='associate_profile_data'),
    url(r'^associate-profile/(?P<slug>[\w-]+)/$', AssociatesProfileView.as_view(), name='associate-profile'),
    url(r'^admin-profile/(?P<slug>[\w-]+)/$', AdminProfileView.as_view(), name='admin-profile'),

    url(r'^store/$', StoreAccountListView.as_view(), name='store-listing'),
    url(r'^store-profile/(?P<slug>[\w-]+)/$', StoreProfileView.as_view(), name='store-profile'),
    url(r'^store-profile-update/$', StoreUpdateView.as_view(), name='store_profile_update'),
    url(r'^store-account-update/$', StoreAccountUpdateView.as_view(), name='store_account_update'),

    url(r'^store_active/$', StoreActiveStatus.as_view(), name='store_active_user'),
    url(r'^store_delete/$', StoreDeleteUsers.as_view(), name='store_delete_users'),

    url(r'^change-password/$', ChangePasswordView.as_view(), name='change_password'),
    url(r'^admin-change-password/$', AdminChangePasswordView.as_view(), name='admin_change_password'),

    url(r'^lead-quotes-list/$', LeadQuotesListView.as_view(), name='lead_listing'),
    url(r'^lead-list/$', LeadListView.as_view(), name='lead_list'),

    url(r'^lead-quotes-profile/(?P<email_slug_field>[\w-]+)/$', LeadQuotesProfileView.as_view(),
        name='lead_quote_profile'),

    url(r'^delete-lead_quote/$', DeleteLeadAndQuote.as_view(), name='delete_lead'),
    url(r'^delete-user/(?P<name_slug_field>[\w-]+)/$', UserDeleteView.as_view(), name='delete_user'),
    url(r'^over-view/$', DashboardView.as_view(), name='dashboard'),
    url(r'^store-wise-view/$', StoreWiseLeadsView.as_view(), name='store-wise-view'),
    url(r'^associate-wise-view/$', AssociateWiseLeadsView.as_view(), name='associate-wise-view'),
]