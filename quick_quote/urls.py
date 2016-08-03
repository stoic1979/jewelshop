"""quick_quote URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings

from rest_framework import routers

from apps.leadquote.viewsets import CustomerViewSet


router = routers.DefaultRouter()
router.register(r'test', CustomerViewSet)

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'django.contrib.auth.views.login', {'redirect_field_name': 'next'},
        name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout',
                           {"next_page": '/'}, name="logout"),
    url(r'^accounts/', include('apps.accounts.urls')),
    url(r'^dashboard/', include('apps.dashboard.urls')),
    url(r'^leadquote/', include('apps.leadquote.urls')),
    url(r'^abc/', include('tests.urls')),
    url(r'^api/', include(router.urls, namespace='api')),
]


urlpatterns += patterns('',
                        url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
                            {'document_root': settings.STATIC_ROOT, 'show_indexes': False}),
                        url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
                            {'document_root': settings.MEDIA_ROOT, 'show_indexes': False}),
                        )
urlpatterns += staticfiles_urlpatterns()