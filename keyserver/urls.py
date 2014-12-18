# coding=utf-8
"""
This File is part of Pinyto
"""

from django.conf.urls import patterns, url

urlpatterns = patterns(
    'keyserver.views',

    url(r'^authenticate$', 'authenticate', name='keyserver_authenticate'),
    url(r'^register$', 'register', name='keyserver_register'),
    url(r'^change_password$', 'change_password', name='change_password'),
)
