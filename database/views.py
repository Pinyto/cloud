# coding=utf-8
"""
This File is part of Pinyto
"""

from django.views.decorators.csrf import csrf_exempt
from pymongo import MongoClient
from pymongo.collection import Collection
from service.response import json_response
from pinytoCloud.checktoken import check_token
from pinytoCloud.models import Session, Assembly
from django.utils import timezone
from database.helpers import get_tags, get_str_or_discard
import json
import time
import pytz


@csrf_exempt
def store(request, user_name, assembly_name):
    """
    Store document in any format. The assembly, date of creation and request.user will be
    added automatically to the document

    @param request: Django request
    @param user_name: string
    @param assembly_name: string
    @return JSON
    """
    try:
        request_data = json.loads(request.body)
    except ValueError:
        return json_response({'error': "Please supply the token as JSON."})
    if 'token' not in request_data:
        return json_response({'error': "Please supply JSON with a token key."})
    session = check_token(request_data['token'])
    # check_token will return an error response if the token is not found or can not be verified.
    if not isinstance(session, Session):
        return session
    # we are authenticated now
    try:
        assembly = Assembly.objects.filter(author__name=user_name).filter(name=assembly_name).all()[0]
    except IndexError:
        return json_response({'error': "The assembly " + user_name + "/" + assembly_name + " does not exist."})
    if assembly not in session.user.installed_assemblies.all():
        return json_response({'error': "The assembly " + user_name + "/" + assembly_name + " is not installed."})
    if 'type' in request_data:
        data_type = get_str_or_discard(str(request_data['type']))
    else:
        data_type = ""
    if 'tags' in request_data:
        tags = get_tags(request_data['tags'])
    else:
        tags = []
    if 'data' in request_data and data_type:
        db = Collection(MongoClient().pinyto, session.user.name)
        document = {'type': data_type,
                    'time': timezone.now().astimezone(pytz.timezone('UTC')),
                    'tags': tags,
                    'assembly': user_name + '/' + assembly_name,
                    'data': request_data['data']}
        db.insert(document)
        return json_response({'success': True})
    else:
        return json_response({'error': "If you want to store data you have to send your " +
                                       "data as json string in the parameter 'data'. " +
                                       "You also have to supply a type string for the data. " +
                                       "Supplying tags in the parameter 'tags' is optional " +
                                       "but strongly recommended."})


@csrf_exempt
def statistics(request):
    """
    Retrieve statistics about storage and computation time usage.

    @param request: Django request
    @return JSON
    """
    try:
        request_data = json.loads(request.body)
    except ValueError:
        return json_response({'error': "Please supply the token as JSON."})
    if 'token' not in request_data:
        return json_response({'error': "Please supply JSON with a token key."})
    session = check_token(request_data['token'])
    # check_token will return an error response if the token is not found or can not be verified.
    if isinstance(session, Session):
        return json_response({
            'time_budget': session.user.time_budget,
            'storage_budget': session.user.storage_budget,
            'current_storage': session.user.current_storage,
            'last_calculation': time.mktime((session.user.last_calculation_time.year,
                                             session.user.last_calculation_time.month,
                                             session.user.last_calculation_time.day,
                                             session.user.last_calculation_time.hour,
                                             session.user.last_calculation_time.minute,
                                             session.user.last_calculation_time.second,
                                             -1, -1, -1)) + session.user.last_calculation_time.microsecond,
            'assembly_count': session.user.assemblies.count(),
            'installed_assemblies_count': session.user.installed_assemblies.count(),
            'all_assemblies_count': Assembly.objects.count()
        })
    else:
        # session is not a session so it has to be response object with an error message
        return session