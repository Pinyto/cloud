# coding=utf-8
"""
This File is part of Pinyto
"""
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from hashlib import sha256
from Crypto.Random import get_random_bytes
import json

from service.response import json_response
from pinytoCloud.models import User, StoredPublicKey, Session
from pinytoCloud.settings import PINYTO_KEY
from pinytoCloud.project_path import project_path
from pinytoCloud.checktoken import check_token


def home(request):
    """
    This view serves static content. Namely index.html which may bootstrap an
    Angular application at the client.

    @param request:
    @return:
    """
    with open(project_path("static/index.html"), 'r') as index_html_file:
        return HttpResponse(index_html_file.read(), content_type='text/html')


@csrf_exempt
def authenticate_request(request):
    """
    Creates a token and registers the authentication request for the username.
    Returns an encrypted token and the matching signature.
    This function only extracts the params from the request and calls authenticate.

    @param request:
    @return: json {encrypted_token: string, signature: string}
    """
    username = request.POST.get('username')
    key_hash = request.POST.get('keyhash')
    if not username or not key_hash:
        return json_response({'error': "You have to supply a username and a keyhash to authenticate."})
    return json_response(authenticate(username, key_hash))


def authenticate(username, key_hash):
    """
    Creates a token and registers the authentication request for the username.
    Returns an encrypted token and the matching signature

    @param username: string
    @param key_hash: string
    @return: json {encrypted_token: string, signature: string}
    """
    try:
        user = User.objects.filter(name=username).all()[0]
    except IndexError:
        return {'error': "User '" + username + "' is unknown. Please register first."}
    try:
        key = user.keys.filter(key_hash=key_hash).all()[0]
    except IndexError:
        return {'error': "This is not a registered public key of this user."}
    session = user.start_session(key)
    encrypted_token = session.get_encrypted_token()
    hasher = sha256()
    hasher.update(encrypted_token)
    signature = PINYTO_KEY.sign(hasher.hexdigest(), get_random_bytes(16))
    return {'encrypted_token': encrypted_token, 'signature': unicode(signature[0])}


@csrf_exempt
def logout(request):
    """
    Ends the session with the given token.

    @param request:
    @return: json
    """
    session = check_token(request.POST.get('token'))
    # check_token will return an error response if the token is not found or can not be verified.
    if isinstance(session, Session):
        session.delete()
    else:
        # session is not a session so it has to be response object with an error message
        return session


@csrf_exempt
def list_keys(request):
    """
    Returns a list of keys for the active account.

    @param request:
    @return: json
    """
    session = check_token(request.POST.get('token'))
    # check_token will return an error response if the token is not found or can not be verified.
    if isinstance(session, Session):
        key_list = []
        for key in session.user.keys.all():
            key_list.append({
                'key_hash': key.key_hash,
                'active': key.active
            })
        return json_response(key_list)
    else:
        # session is not a session so it has to be response object with an error message
        return session


@csrf_exempt
def set_key_active(request):
    """
    Sets the transferred active state for the key.

    @param request:
    @return: json
    """
    session = check_token(request.POST.get('token'))
    # check_token will return an error response if the token is not found or can not be verified.
    if isinstance(session, Session):
        if not 'key_hash' in request.POST or not 'active_state' in request.POST:
            return json_response({'error': "You have to supply a key_hash and an active_state."})
        if session.user.keys.filter(active=True).exclude(key_hash=request.POST['key_hash']).count() < 1:
            return json_response(
                {'error': "You are deactivating your last active key. " +
                          "That is in all possible scenarios a bad idea so it will not be done."}
            )
        key = session.user.keys.get(key_hash=request.POST['key_hash'])
        if request.POST['active_state']:
            key.active = True
        else:
            key.active = False
        key.save()
        return json_response({'success': True})
    else:
        # session is not a session so it has to be response object with an error message
        return session


@csrf_exempt
def delete_key(request):
    """
    Deletes the specified key. This will raise an error if you try to delete your last key.

    @param request: Django request
    @return: json
    """
    session = check_token(request.POST.get('token'))
    # check_token will return an error response if the token is not found or can not be verified.
    if isinstance(session, Session):
        if not 'key_hash' in request.POST:
            return json_response({'error': "You have to supply a key_hash."})
        if session.user.keys.filter(active=True).exclude(key_hash=request.POST['key_hash']).count() < 1:
            return json_response(
                {'error': "You are deleting your last active key. " +
                          "That is in all possible scenarios a bad idea so it will not be done."}
            )
        key = session.user.keys.get(key_hash=request.POST['key_hash'])
        key.delete()
        return json_response({'success': True})
    else:
        # session is not a session so it has to be response object with an error message
        return session


@csrf_exempt
def register_request(request):
    """
    Creates an account if possible and saves the public key.
    This function only extracts the params from the request and calls register.

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
    return json_response(register(username, key_data))


def register(username, key_data):
    """
    Creates an account if possible and saves the public key.

    @param username: string
    @param key_data: string
    @return: json
    """
    if User.objects.filter(name=username).count() > 0:
        return {'error': "Username " + username + " is already taken. Try another username."}
    if not 'N' in key_data or not 'e' in key_data:
        return {'error': "The public_key is in the wrong format. The key data must consist of an N and an e."}
    try:
        n = long(key_data['N'])
        if n < pow(2, 3071):
            return {'error': "Factor N in the public key is too small. Please use 3072 bit."}
    except ValueError:
        return {'error': "Factor N in the public key is not a number. It has to be a long integer."}
    try:
        e = long(key_data['e'])
    except ValueError:
        return {'error': "Factor e in the public key is not a number. It has to be a long integer."}
    new_user = User(name=username)
    new_user.save()
    StoredPublicKey.create(new_user, unicode(key_data['N']), e)
    return {'success': True}