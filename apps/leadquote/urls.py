from django.conf.urls import url

from .views import CustomerView, JewelleryTypeView, PremiumSelectView, EmailSendView

urlpatterns = [
    url(r'^jewelry-insurance-customer-details/(?P<slug>[-\w]+)/$', CustomerView.as_view(), name='customer-details'),
    url(r'^jewelry-insurance-select-types/(?P<slug>[-\w]+)/(?P<email_slug>[-\w]+)/$', JewelleryTypeView.as_view(),
        name='jewellery-type'),
    url(r'^jewelry-insurance-premium-rates/(?P<email_slug>[-\w]+)/(?P<slug>[-\w]+)/$', PremiumSelectView.as_view(),
        name='premium_content'),

    url(r'^customer-email-send/$', EmailSendView.as_view(), name='send-email'),


        ]