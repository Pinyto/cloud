# coding=utf-8
"""
This File is part of Pinyto
"""
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
#from django.contrib.auth import authenticate, login as backend_login, logout as backend_logout
from pinytoCloud.models import User, StoredPublicKey
from Crypto.Random import get_random_bytes
from django.core.context_processors import csrf
from project_path import project_path
from pymongo import MongoClient
from pymongo.collection import Collection
from service.response import json_response
from datetime import datetime
from hashlib import sha256
from database.helpers import get_tags, get_str_or_discard
from pinytoCloud.settings import PINYTO_KEY
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
def authenticate(request):
    """
    Creates a token and registers the authentication request for the username.
    Returns an encrypted token and the matching signature

    @param request:
    @return: json {encrypted_token: string, signature: string}
    """
    username = request.POST.get('username')
    key_hash = request.POST.get('keyhash')
    try:
        user = User.objects.filter(name=username).all()[0]
    except IndexError:
        return json_response({'error': "User '" + username + "' is unknown. Please register first."})
    try:
        key = user.keys.filter(key_hash=key_hash).all()[0].get_key()
    except IndexError:
        return json_response({'error': "This is not a registered public key of this user."})
    user.start_session()
    encrypted_token = user.session.get_encrypted_token(key)
    hasher = sha256()
    hasher.update(encrypted_token)
    signature = PINYTO_KEY.sign(hasher.hexdigest(), get_random_bytes(16))
    return json_response({'encrypted_token': encrypted_token, 'signature': unicode(signature[0])})


@csrf_exempt
def register(request):
    """
    Creates an account if possible and saves the public key.

    @param request:
    @return: json
    """
    username = request.POST.get('username')
    if not username:
        return json_response({'error': "You have to supply a username."})
    try:
        key_data = json.loads(request.POST.get('public_key'))
    except TypeError:
        return json_response({'error': "You have to supply a public_key."})
    if User.objects.filter(name=username).count() > 0:
        return json_response({'error': "Username '" + username + "' is already taken. Try another username."})
    if not 'N' in key_data or not 'e' in key_data:
        return json_response(
            {'error': "The public_key is in the wrong format. The key data must consist of an N and an e."}
        )
    try:
        n = long(key_data['N'])
        if n < pow(2, 3071):
            return json_response({'error': "Factor N in the public key is too small. Please use 3072 bit."})
    except ValueError:
        return json_response({'error': "Factor N in the public key is not a number. It has to be a long integer."})
    try:
        e = long(key_data['e'])
    except ValueError:
        return json_response({'error': "Factor e in the public key is not a number. It has to be a long integer."})
    new_user = User(name=username)
    new_user.save()
    StoredPublicKey.create(new_user, unicode(key_data['N']), e)
    return json_response({'success': True})


@csrf_exempt
def login(request):
    """
    Login to the cloud. This also selects the collection (username).

    @param request:
    @return:
    """
    # user = authenticate(username=request.POST.get('username'), password=request.POST.get('password'))
    # backend_logout(request)
    # if user is not None:
    #     # the password verified for the user
    #     if user.is_active:
    #         backend_login(request, user)
    #         return json_response({'authenticated': True,
    #                               'csrf_token': unicode(csrf(request)['csrf_token'])})
    #     else:
    #         return json_response({'authenticated': False,
    #                               'error': "The password is valid, but the account has been disabled!"})
    # else:
    #     # the authentication system was unable to verify the username and password
    #     return json_response({'authenticated': False,
    #                           'error': "The username and password were incorrect."})


def store(request):
    """
    Store document in any format. The date of creation and request.user will be
    added automatically to the document

    :param request:
    """
    if request.user.is_authenticated():
        data = request.POST.get('data')
        data_type = get_str_or_discard(request.POST.get('type'))
        tags = request.POST.get('tags')
        if data and data_type:
            db = Collection(MongoClient().pinyto, request.user.username)
            document = {'type': data_type,
                        'time': datetime.utcnow(),
                        'tags': get_tags(json.loads(tags)),
                        'data': json.loads(data)}
            db.insert(document)
            return json_response({'success': True})
        else:
            return json_response({'error': "If you want to store data you have to send your " +
                                           "data as json string in a POST request in the parameter 'data'. " +
                                           "You also have to supply a type string for the data. " +
                                           "Supplying tags in the parameter 'tags' is optional " +
                                           "but strongly recommended."})
    else:
        return json_response({'error': "You have to log in before you are allowed to store data."})