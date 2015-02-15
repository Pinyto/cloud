# coding=utf-8
"""
This File is part of Pinyto
"""
from django.dispatch import receiver
from django.core.signals import request_finished
from django.http import HttpResponse
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.son_manipulator import ObjectId
from service.database import CollectionWrapper
from service.response import json_response
from service.models import Factory as DirectFactory
from pinytoCloud.checktoken import check_token
from pinytoCloud.models import Session
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
        return json_response({'error': "All Pinyto API-calls have to use json. This is not valid JSON data."})
    if 'token' not in json_data:
        return json_response({'error': "Unauthenticated API-calls are not supported. Please supply a token."})
    session = check_token(json_data['token'])
    if not isinstance(session, Session):
        # session is not a session so it has to be response object with an error message
        return session
    try:
        assembly_user = User.objects.filter(name=user_name).all()[0]
    except IndexError:
        return json_response(
            {'error': "The user " + user_name + " was not found. There can not be an assembly " +
                      user_name + "/" + assembly_name + "."}
        )
    try:
        assemblies = assembly_user.assemblies.filter(name=assembly_name).all()
        if len(assemblies) > 1:  # This can't occur because assembly name + user are unique together
            return json_response(
                {'error': "The user has more than one assembly of this name. That does not make any sense."}
            )
        assembly = assemblies[0]
    except IndexError:
        return json_response(
            {'error': "Assembly not found. Does " + assembly_user.name + " have an Assembly named " +
                      assembly_name + "?"}
        )
    if assembly not in session.user.installed_assemblies.all():
        return json_response({'error': "The assembly exists but it is not installed."})
    # Try to load statically defined api functions.
    try:
        api_class = getattr(import_module('api.' + user_name + '_' + assembly_name + '.assembly'), assembly_name)
    except ImportError:
        # There is no statically defined api function for this call. Proceed to
        # loading the code from the database and executing it in the sandbox.
        return load_api(request, session=session, assembly=assembly, function_name=function_name)
    for name, function in getmembers(api_class, predicate=isfunction):
        if not name.startswith('job_') and name == function_name:
            if session.user.name in MongoClient().pinyto.collection_names():
                collection = Collection(MongoClient().pinyto, session.user.name)
            else:
                collection = Collection(MongoClient().pinyto, session.user.name, create=True)
            collection_wrapper = CollectionWrapper(
                collection,
                assembly_name=user_name + '/' + assembly_name,
                only_own_data=assembly.only_own_data)
            start_time = time.clock()
            response = function(request, collection_wrapper, DirectFactory())
            end_time = time.clock()
            session.user.calculate_time_and_storage(
                end_time - start_time,
                MongoClient().pinyto.command('collstats', session.user.name)['size']
            )
            return HttpResponse(response, content_type='application/json')
    # If we reach this point the api_class was found but the function was not defined in the class.
    # So we try to load this code from the database.
    return load_api(request, session=session, assembly=assembly, function_name=function_name)


def load_api(request, session, assembly, function_name):
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
    if session.user.name in MongoClient().pinyto.collection_names():
        collection = Collection(MongoClient().pinyto, session.user.name)
    else:
        collection = Collection(MongoClient().pinyto, session.user.name, create=True)
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
        MongoClient().pinyto.command('collstats', session.user.name)['size']
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
    for user in User.objects.all():
        collection = Collection(MongoClient().pinyto, user.name)
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
                collection.remove(spec_or_id={"_id": ObjectId(job['_id'])})
                user.calculate_time_and_storage(
                    elapsed_time,
                    MongoClient().pinyto.command('collstats', user.name)['size']
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
                    collection.remove(spec_or_id={"_id": ObjectId(job['_id'])})
                    end_time = time.clock()
                    user.calculate_time_and_storage(
                        end_time - start_time,
                        MongoClient().pinyto.command('collstats', user.name)['size']
                    )