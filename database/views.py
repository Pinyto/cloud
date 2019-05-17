# coding=utf-8
"""
Pinyto cloud - A secure cloud database for your personal data
Copyright (C) 2105 Johannes Merkert <jonny@pinyto.de>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from django.views.decorators.csrf import csrf_exempt
from database.mongo_connection import MongoConnection
from pymongo.collection import Collection
from service.response import json_response, json_bad_request_response, json_not_found_response
from pinytoCloud.checktoken import check_token, PinytoTokenError
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

    :param request: Django request
    :type request: HttpRequest
    :param user_name:
    :type user_name: str
    :param assembly_name:
    :type assembly_name: str
    :return: JSON
    :rtype: str
    """
    try:
        request_data = json.loads(str(request.body, encoding='utf-8'))
    except ValueError:
        return json_bad_request_response({'error': "Please supply the token as JSON."})
    if 'token' not in request_data:
        return json_bad_request_response({'error': "Please supply JSON with a token key."})
    try:
        session = check_token(request_data['token'])
    except PinytoTokenError as e:
        return json_bad_request_response(e.error_json)
    # we are authenticated now
    try:
        assembly = Assembly.objects.filter(author__name=user_name).filter(name=assembly_name).all()[0]
    except IndexError:
        return json_not_found_response(
            {'error': "The assembly " + user_name + "/" + assembly_name + " does not exist."})
    if assembly not in session.user.installed_assemblies.all():
        return json_not_found_response(
            {'error': "The assembly " + user_name + "/" + assembly_name + " is not installed."})
    if 'type' in request_data:
        data_type = get_str_or_discard(str(request_data['type']))
    else:
        data_type = ""
    if 'tags' in request_data:
        tags = get_tags(request_data['tags'])
    else:
        tags = []
    if 'data' in request_data and data_type:
        db = Collection(MongoConnection.get_db(), session.user.name)
        document = {'type': data_type,
                    'time': timezone.now().astimezone(pytz.timezone('UTC')),
                    'tags': tags,
                    'assembly': user_name + '/' + assembly_name,
                    'data': request_data['data']}
        db.insert_one(document)
        return json_response({'success': True})
    else:
        return json_bad_request_response(
            {'error': "If you want to store data you have to send your " +
                      "data as json string in the parameter 'data'. " +
                      "You also have to supply a type string for the data. " +
                      "Supplying tags in the parameter 'tags' is optional " +
                      "but strongly recommended."})


@csrf_exempt
def statistics(request):
    """
    Retrieve statistics about storage and computation time usage.

    :param request: Django request
    :type request: HttpRequest
    :return: JSON
    :rtype: str
    """
    try:
        request_data = json.loads(str(request.body, encoding='utf-8'))
    except ValueError:
        return json_bad_request_response({'error': "Please supply the token as JSON."})
    if 'token' not in request_data:
        return json_bad_request_response({'error': "Please supply JSON with a token key."})
    try:
        session = check_token(request_data['token'])
    except PinytoTokenError as e:
        return json_bad_request_response(e.error_json)
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
