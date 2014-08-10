# coding=utf-8
"""
This File is part of Pinyto
"""
from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns(
    'pinytoCloud.views',

    url(r'^authenticate$', 'authenticate', name='authenticate'),
    url(r'^register$', 'register', name='register'),
)

urlpatterns += patterns(
    'database.views',

    url(r'^store$', 'store', name='store'),
)

urlpatterns += patterns(
    'api_prototype.views',

    url(r'^(?P<user_name>\w+)/(?P<assembly_name>\w+)/(?P<function_name>\w+)$', 'api_call', name='api_call'),
    #url(r'^$', 'load', name='load'),
)

urlpatterns += patterns(
    'pinytoCloud.views',

    url(r'^.*', 'home', name='home'),
)