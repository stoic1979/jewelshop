from django.conf.urls import url

from .views import SignUpView, ActivationView, SetUserRoleView, AssociateFieldCheckView, ForgotPassword

urlpatterns = [
    url(r'^sign-up/$', SignUpView.as_view(), name='sign-up'),
    url(r'^accociate-field-check/$', AssociateFieldCheckView.as_view(), name='associate-field-check'),
    url(r'^user-role-setting/$', SetUserRoleView.as_view(), name='user-role'),
    url(r'^activate-user/(?P<slug>[-\w]+)/$', ActivationView.as_view(), name='activate-user'),
    # url(r'^edit-profile/(?P<pk>[-\d]+)/$', UserUpdateView.as_view(), name='edit-profile'),
    # url(r'^edit-profile/(?P<pk>[-\d]+)/$', EditProfileView.as_view(), name='edit-profile'),
    url(r'^forgot-password/$', ForgotPassword.as_view(), name='user_forgot_password'),


        ]