# coding=utf-8
"""
This File is part of Pinyto
"""

from django.views.decorators.csrf import csrf_exempt
from hashlib import sha256
from Crypto.Random import get_random_bytes
import json

from service.response import json_response
from pinytoCloud.models import User, StoredPublicKey
from pinytoCloud.settings import PINYTO_KEY

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
        key = user.keys.filter(key_hash=key_hash).all()[0]
    except IndexError:
        return json_response({'error': "This is not a registered public key of this user."})
    session = user.start_session(key)
    encrypted_token = session.get_encrypted_token()
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
        return json_response({'error': "Username " + username + " is already taken. Try another username."})
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