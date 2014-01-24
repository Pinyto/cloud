# coding=utf-8
"""
This File is part of Pinyto
"""
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login as backend_login
from project_path import project_path
from pymongo import MongoClient
from pymongo.collection import Collection
from service.response import json_response
from datetime import datetime
import json


def home(request):
    """
    This should not be necessary.
    @param request:
    @return:
    """
    with open(project_path("static/index.html"), 'r') as index_html_file:
        return HttpResponse(index_html_file.read(), mimetype='text/html')


@csrf_exempt
def login(request):
    """
    Login to the cloud. This also selects the collection (username).

    @param request:
    @return:
    """
    user = authenticate(username=request.POST.get('username'), password=request.POST.get('password'))
    if user is not None:
        # the password verified for the user
        if user.is_active:
            backend_login(request, user)
            return json_response({'authenticated': True})
        else:
            return json_response({'authenticated': False,
                                  'error': "The password is valid, but the account has been disabled!"})
    else:
        # the authentication system was unable to verify the username and password
        return json_response({'authenticated': False,
                              'error': "The username and password were incorrect."})


@csrf_exempt
def store(request):
    """
    Store document in any format. The date of creation and request.user will be
    added automatically to the document

    :param request:
    """
    if request.user.is_authenticated():
        data = request.POST.get('data')
        data_type = request.POST.get('type')
        if data and data_type:
            db = Collection(MongoClient().pinyto, request.user.username)
            document = {'type': data_type,
                        'time': datetime.utcnow(),
                        'data': json.loads(data)}
            db.insert(document)
            return json_response({'success': True})
        else:
            return json_response({'error': "If you want to store data you have to send your " +
                                           "data as json string in a POST request in the parameter 'data'. " +
                                           "You also have to supply a type string for the data."})
    else:
        return json_response({'error': "You have to log in before you are allowed to store data."})