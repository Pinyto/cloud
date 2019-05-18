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

from django.dispatch import receiver
from django.core.signals import request_finished
from django.http import HttpResponse
from database.mongo_connection import MongoConnection
from pymongo.collection import Collection
from pymongo.son_manipulator import ObjectId
from service.database import CollectionWrapper
from service.response import json_response, json_bad_request_response, json_not_found_response
from service.models import Factory as DirectFactory
from pinytoCloud.checktoken import check_token, PinytoTokenError
from pinytoCloud.models import User
from api_prototype.sandbox import safely_exec
from api_prototype.sandbox_helpers import EmptyRequest
from importlib import import_module
from inspect import getmembers, isfunction
import time
import json


def api_call(request, user_name, assembly_name, function_name):
    """
    This selects a ApiFunction and executes it if possible.

    :param request: Django Request object
    :type request: HttpRequest
    :param user_name:
    :type user_name: str
    :param assembly_name:
    :type assembly_name: str
    :param function_name:
    :type function_name: str
    :return: json response
    :rtype: HttpResponse
    """
    try:
        json_data = json.loads(str(request.body, encoding='utf-8'))
    except ValueError:
        return json_bad_request_response(
            {'error': "All Pinyto API-calls have to use json. This is not valid JSON data."})
    if 'token' not in json_data:
        return json_bad_request_response(
            {'error': "Unauthenticated API-calls are not supported. Please supply a token."})
    try:
        session = check_token(json_data['token'])
    except PinytoTokenError as e:
        return json_bad_request_response(e.error_json)
    try:
        assembly_user = User.objects.filter(name=user_name).all()[0]
    except IndexError:
        return json_not_found_response(
            {'error': "The user " + user_name + " was not found. There can not be an assembly " +
                      user_name + "/" + assembly_name + "."}
        )
    try:
        assemblies = assembly_user.assemblies.filter(name=assembly_name).all()
        if len(assemblies) > 1:  # This can't occur because assembly name + user are unique together
            return json_bad_request_response(
                {'error': "The user has more than one assembly of this name. That does not make any sense."}
            )
        assembly = assemblies[0]
    except IndexError:
        return json_not_found_response(
            {'error': "Assembly not found. Does " + assembly_user.name + " have an Assembly named " +
                      assembly_name + "?"}
        )
    if assembly not in session.user.installed_assemblies.all():
        return json_not_found_response({'error': "The assembly exists but it is not installed."})
    mongo_db = MongoConnection.get_db()
    # Try to load statically defined api functions.
    try:
        api_class = getattr(import_module('api.' + user_name + '_' + assembly_name + '.assembly'), assembly_name)
    except ImportError:
        # There is no statically defined api function for this call. Proceed to
        # loading the code from the database and executing it in the sandbox.
        return load_api(request, session=session, assembly=assembly, function_name=function_name,
                        mongo_db=mongo_db)
    for name, function in getmembers(api_class, predicate=isfunction):
        if not name.startswith('job_') and name == function_name:
            if session.user.name in mongo_db.collection_names():
                collection = Collection(mongo_db, session.user.name)
            else:
                collection = Collection(mongo_db, session.user.name, create=True)
            collection_wrapper = CollectionWrapper(
                collection,
                assembly_name=user_name + '/' + assembly_name,
                only_own_data=assembly.only_own_data)
            start_time = time.clock()
            response_json = function(request, collection_wrapper, DirectFactory())
            end_time = time.clock()
            session.user.calculate_time_and_storage(
                end_time - start_time,
                MongoConnection.get_db().command('collstats', session.user.name)['size']
            )
            if 'error' in response_json:
                return json_bad_request_response(response_json)
            else:
                return json_response(response_json)
    # If we reach this point the api_class was found but the function was not defined in the class.
    # So we try to load this code from the database.
    return load_api(request, session=session, assembly=assembly, function_name=function_name,
                    mongo_db=mongo_db)


def load_api(request, session, assembly, function_name, mongo_db=MongoConnection.get_db()):
    """
    There is no statically defined api function for this call. Proceed to
    loading the code from the database and executing it in the sandbox.

    :param request: Django Request object
    :type request: HttpRequest
    :param session:
    :type session: pinytoCloud.models.Session
    :param assembly:
    :type assembly: pinytoCloud.models.Assembly
    :param function_name:
    :type function_name: str
    :param mongo_db:
    :type mongo_db: pymongo.database.Database
    :return: json response
    :rtype: HttpResponse
    """
    try:
        api_function = assembly.api_functions.filter(name=function_name).all()[0]
    except IndexError:
        return json_response(
            {'error': "The assembly " + assembly.author.name + "/" + assembly.name +
                      ' exists but has no API function "' + function_name + '".'}
        )
    if session.user.name in mongo_db.collection_names():
        collection = Collection(mongo_db, session.user.name)
    else:
        collection = Collection(mongo_db, session.user.name, create=True)
    collection_wrapper = CollectionWrapper(
        collection,
        assembly_name=assembly.author.name + '/' + assembly.name,
        only_own_data=assembly.only_own_data)
    response_data, elapsed_time = safely_exec(api_function.code, request, collection_wrapper)
    if 'result' in response_data:
        response_data = response_data['result']
    else:
        response_data = json.dumps(response_data)
    session.user.calculate_time_and_storage(
        elapsed_time,
        mongo_db.command('collstats', session.user.name)['size']
    )
    return HttpResponse(response_data, content_type='application/json')


@receiver(request_finished)
def check_for_jobs(sender, **kwargs):
    """
    Check in the collection of all users if there are any scheduled jobs.

    This is done with a query for documents of the "type": "job". If documents are found the job specified
    by the document gets executed. The document describing the job gets deleted after the execution.

    :param sender:
    :param kwargs:
    """
    mongo_db = MongoConnection.get_db()
    for user in User.objects.all():
        collection = Collection(mongo_db, user.name)
        for job in collection.find({'type': 'job'}):
            if 'data' not in job or 'assembly_user' not in job['data'] or 'assembly_name' not in job['data'] or \
               'job_name' not in job['data']:  # TODO: Check that the job is from the correct assembly.
                continue
            try:
                assembly = User.objects.filter(
                    name=job['data']['assembly_user']
                ).all()[0].assemblies.filter(name=job['data']['assembly_name']).all()[0]
            except IndexError:
                return json_response(
                    {'error': "Assembly not found. Does " + job['data']['assembly_user'] +
                              " have an Assembly named " + job['data']['assembly_name'] + "?"}
                )
            try:
                api_class = getattr(
                    import_module(
                        'api.' + job['data']['assembly_user'] + '_' + job['data']['assembly_name'] + '.assembly'
                    ), job['data']['assembly_name'])
            except ImportError:
                # There is no statically defined api function for this call. Proceed to
                # loading the code from the database and executing it in the sandbox.
                try:
                    api_function = assembly.jobs.filter(name=job['data']['job_name']).all()[0]
                except IndexError:
                    return json_response(
                        {'error': "The assembly " + job['data']['assembly_user'] + "/" +
                                  job['data']['assembly_name'] + ' exists but has no job "' +
                                  job['data']['job_name'] + '" defined.'}
                    )
                collection_wrapper = CollectionWrapper(
                    collection,
                    assembly_name=job['data']['assembly_user'] + '/' + job['data']['assembly_name'],
                    only_own_data=assembly.only_own_data)
                response_data, elapsed_time = safely_exec(api_function.code, EmptyRequest(), collection_wrapper)
                collection.delete_one(filter={"_id": ObjectId(job['_id'])})
                user.calculate_time_and_storage(
                    elapsed_time,
                    mongo_db.command('collstats', user.name)['size']
                )
                continue
            for name, function in getmembers(api_class, predicate=isfunction):
                if name.startswith('job_') and name == job['data']['job_name']:
                    collection_wrapper = CollectionWrapper(
                        collection,
                        assembly_name=job['data']['assembly_user'] + '/' + job['data']['assembly_name'],
                        only_own_data=assembly.only_own_data)
                    start_time = time.clock()
                    function(collection_wrapper, DirectFactory())
                    collection.delete_one(filter={"_id": ObjectId(job['_id'])})
                    end_time = time.clock()
                    user.calculate_time_and_storage(
                        end_time - start_time,
                        mongo_db.command('collstats', user.name)['size']
                    )
