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
from models import Factory as SandboxFactory
from service.models import Factory as DirectFactory
from pinytoCloud.checktoken import check_token
from pinytoCloud.models import Session
from pinytoCloud.models import User
from sandbox import safely_exec
from inspect import getmembers, isfunction
import time

ApiClasses = [('librarian.views', 'Librarian')]


def api_call(request, user_name, assembly_name, function_name):
    """
    This selects a ApiFunction and executes it if possible.

    @param user_name: string
    @param assembly_name: string
    @param function_name: string
    @param request: Django Request object
    @return: json response
    """
    token = request.POST.get('token')
    if not token:
        return json_response({'error': "Unauthenticated API-calls are not supported. Please supply a token."})
    session = check_token(token)
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
    # Try to load statically defined api functions.
    try:
        api_class = getattr(__import__('api.' + user_name, fromlist=[assembly_name]), assembly_name)
    except ImportError:
        # There is no statically defined api function for this call. Proceed to
        # loading the code from the database and executing it in the sandbox.
        return load_api(request, session, assembly_user, assembly_name, function_name)
    for name, function in getmembers(api_class, predicate=isfunction):
        if not unicode(name).startswith(u'job_') and unicode(name) == unicode(function_name):
            collection = Collection(MongoClient().pinyto, session.user.name)
            collection_wrapper = CollectionWrapper(collection)
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
    return load_api(session, assembly_user, assembly_name, function_name)


def load_api(request, session, assembly_user, assembly_name, function_name):
    """
    There is no statically defined api function for this call. Proceed to
    loading the code from the database and executing it in the sandbox.

    @param request: Django's request object
    @param session: Session
    @param assembly_user: User
    @param assembly_name: string
    @param function_name: string
    @return: Response object
    """
    try:
        assemblies = assembly_user.assemblies.filter(name=assembly_name).all()
        if len(assemblies) > 1:
            return json_response(
                {'error': "The user has more than one assembly of this name. That does not make any sense."}
            )
        assembly = assemblies[0]
    except IndexError:
        return json_response(
            {'error': "Assembly not found. Does " + assembly_user.name + " have an Assembly named " +
                      assembly_name + "?"}
        )
    try:
        api_function = assembly.api_functions.filter(name=function_name).all()[0]
    except IndexError:
        return json_response(
            {'error': "The assembly " + assembly_user.name + "/" + assembly_name + ' exists but has no API function "' +
                      function_name + '".'}
        )
    collection = Collection(MongoClient().pinyto, session.user.name)
    collection_wrapper = CollectionWrapper(collection)
    response_data, elapsed_time = safely_exec(api_function.code, request, collection_wrapper)
    session.user.calculate_time_and_storage(
        elapsed_time,
        MongoClient().pinyto.command('collstats', session.user.name)['size']
    )
    return HttpResponse(response_data, content_type='application/json')


@receiver(request_finished)
def check_for_jobs(sender, **kwargs):
    """
    Check in the collection of all users if there are any scheduled jobs.

    @param sender:
    @param kwargs:
    """
    for user in User.objects.all():
        collection = Collection(MongoClient().pinyto, user.name)
        for job in collection.find({'type': 'job'}):
            if not job['data'] or not job['data']['assembly_user'] or not job['data']['assembly_name'] or \
               not job['data']['job_name']:
                continue
            try:
                api_class = getattr(
                    __import__(
                        'api.' + job['data']['assembly_user'],
                        fromlist=[job['data']['assembly_name']]),
                    job['data']['assembly_name'])
            except ImportError:
                # There is no statically defined api function for this call. Proceed to
                # loading the code from the database and executing it in the sandbox.
                try:
                    assemblies = User.objects.filter(
                        name=job['data']['assembly_user']
                    ).all()[0].assemblies.filter(name=job['data']['assembly_name']).all()
                    if len(assemblies) > 1:
                        return json_response(
                            {'error': "The user has more than one assembly of this name. That does not make any sense."}
                        )
                    assembly = assemblies[0]
                except IndexError:
                    return json_response(
                        {'error': "Assembly not found. Does " + job['data']['assembly_user'] + " have an Assembly named " +
                                  job['data']['assembly_name'] + "?"}
                    )
                try:
                    api_function = assembly.jobs.filter(name=job['data']['job_name']).all()[0]
                except IndexError:
                    return json_response(
                        {'error': "The assembly " + job['data']['assembly_user'] + "/" +
                                  job['data']['assembly_name'] + ' exists but has no job "' +
                                  job['data']['job_name'] + '" defined.'}
                    )
                collection_wrapper = CollectionWrapper(collection)
                response_data, elapsed_time = safely_exec(api_function.code, None, collection_wrapper)
                collection.remove(spec_or_id={"_id": ObjectId(job['_id'])})
                user.calculate_time_and_storage(
                    elapsed_time,
                    MongoClient().pinyto.command('collstats', user.name)['size']
                )
                continue
            for name, function in getmembers(api_class, predicate=isfunction):
                if unicode(name).startswith(u'job_') and unicode(name) == unicode(job['data']['job_name']):
                    collection_wrapper = CollectionWrapper(collection)
                    start_time = time.clock()
                    function(collection_wrapper, DirectFactory())
                    collection.remove(spec_or_id={"_id": ObjectId(job['_id'])})
                    end_time = time.clock()
                    user.calculate_time_and_storage(
                        end_time - start_time,
                        MongoClient().pinyto.command('collstats', user.name)['size']
                    )