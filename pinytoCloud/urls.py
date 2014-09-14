# coding=utf-8
"""
This File is part of Pinyto
"""
from django.conf.urls import patterns, include, url

urlpatterns = patterns(
    'pinytoCloud.views',

    url(r'^authenticate$', 'authenticate_request', name='authenticate'),
    url(r'^logout$', 'logout', name='logout'),
    url(r'^list_keys$', 'list_keys', name='list_keys'),
    url(r'^set_key_active$', 'set_key_active', name='set_key_active'),
    url(r'^delete_key$', 'delete_key', name='delete_key'),
    url(r'^register$', 'register_request', name='register'),
    url(r'^list_own_assemblies$', 'list_own_assemblies', name='list_own_assemblies'),
)

urlpatterns += patterns(
    '',

    url(r'^keyserver/', include('keyserver.urls')),
)

urlpatterns += patterns(
    'database.views',

    url(r'^store$', 'store', name='store'),
    url(r'^statistics$', 'statistics', name='statistics'),
)

urlpatterns += patterns(
    'api_prototype.views',

    url(r'^(?P<user_name>\w+)/(?P<assembly_name>\w+)/(?P<function_name>\w+)$', 'api_call', name='api_call'),
)

urlpatterns += patterns(
    'pinytoCloud.views',

    url(r'^.*', 'home', name='home'),
)