# coding=utf-8
"""
This File is part of Pinyto
"""
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.son_manipulator import ObjectId
from service.database import encode_underscore_fields_list, CollectionWrapper
from service.response import json_response
from pinytoCloud.checktoken import check_token
from pinytoCloud.models import Session
from datetime import datetime
from pinytoCloud.models import User
from sandbox import safely_exec
from inspect import getmembers, isfunction
from django.http import HttpResponse

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
        return load_api(session, assembly_user, assembly_name, function_name)
    for name, function in getmembers(api_class, predicate=isfunction):
        if not unicode(name).startswith(u'job_') and unicode(name) == unicode(function_name):
            collection = Collection(MongoClient().pinyto, session.user.name)
            collection_wrapper = CollectionWrapper(collection)
            return HttpResponse(
                function(
                    request,
                    collection_wrapper
                ),
                content_type='application/json')
    # If we reach this point the api_class was found but the function was not defined in the class.
    # So we try to load this code from the database.
    return load_api(session, assembly_user, assembly_name, function_name)


def load_api(session, assembly_user, assembly_name, function_name):
    """
    There is no statically defined api function for this call. Proceed to
    loading the code from the database and executing it in the sandbox.

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
    print(api_function.code)
    collection = Collection(MongoClient().pinyto, session.user.name)
    collection_wrapper = CollectionWrapper(collection)
    response_data, time = safely_exec(api_function.code, collection_wrapper)  # TODO: pass response object
    print(time)
    return json_response(response_data)


def check_for_jobs(collection_wrapper):
    """
    Check in the collection of the user if there are any scheduled jobs. These get
    executed in the order of their creation.

    @param collection_wrapper: CollectionWrapper
    @return:
    """

    pass