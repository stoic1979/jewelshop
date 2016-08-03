from django.conf.urls import url

from .views import SignIn, About, Welcome, ChooseDeduct, LetsStart

urlpatterns = [
    url(r'^signin/$', SignIn.as_view(), name='signin'),
    url(r'^about/$', About.as_view(), name='about'),
    url(r'^welcome/$', Welcome.as_view(), name='welcome'),
    url(r'^chooseDeductible/$', ChooseDeduct.as_view(), name='chooseDeductible'),
    url(r'^letsStart/$', LetsStart.as_view(), name='letsStart'),
]