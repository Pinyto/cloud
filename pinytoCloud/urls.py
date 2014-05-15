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
    #url(r'^\.login$', 'login', name='login'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),

    #url(r'^[^.].*', 'home', name='home'),
    #url(r'^$', 'home', name='home'),
)

urlpatterns += patterns(
    'api_prototype.views',

    url(r'^[^.].*', 'load', name='load'),
    url(r'^$', 'load', name='load'),
)