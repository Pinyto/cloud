# coding=utf-8
"""
This File is part of Pinyto
"""

from keyserver.models import Account
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from hashlib import sha256
from base64 import b16decode, b16encode
from django.http import HttpResponse
import json
from settings import PINYTO_PUBLICKEY
from pinytoCloud.views import authenticate as cloud_authenticate
from pinytoCloud.views import register as cloud_register
from pinytoCloud.checktoken import check_token
from pinytoCloud.models import Session


def authenticate(request):
    """
    Authenticate at the keyserver.

    @param request:
    @return:
    """
    if not 'name' in request.POST or not 'password' in request.POST:
        return HttpResponse(
            json.dumps({'error': "Please supply username and password as POST parameters. Authentication failed."}),
            content_type='application/json'
        )
    name = request.POST['name']
    password = request.POST['password']
    try:
        account = Account.objects.filter(name=name).all()[0]
    except IndexError:
        return HttpResponse(
            json.dumps({'error': name + " is not a valid account name. Authentication failed."}),
            content_type='application/json'
        )
    if not account.check_password(password):
        return HttpResponse(
            json.dumps({'error': "Wrong password. Authentication failed."}),
            content_type='application/json'
        )
    # Make a request to Pinyto-Cloud asking for a encrypted token
    hasher = sha256()
    hasher.update(account.N + str(account.e))
    response = cloud_authenticate(name, hasher.hexdigest()[:10])
    if 'error' in response:
        return HttpResponse(
            json.dumps({'error': "Cloud Error: " + response['error'] + " Authentication failed."}),
            content_type='application/json'
        )
    if not 'encrypted_token' in response:
        return HttpResponse(
            json.dumps({'error': "Malformatted Response of the Pinyto-Cloud. Authentication failed."}),
            content_type='application/json'
        )
    encrypted_token = response['encrypted_token']
    signature = (long(response['signature']),)
    hasher = sha256()
    hasher.update(encrypted_token)
    if not PINYTO_PUBLICKEY.verify(hasher.hexdigest(), signature):
        return HttpResponse(json.dumps(
            {'error': "Pinyto-Cloud signature is wrong. This is a man-in-the-middle-attack! "
                      + "The developers will be informed. Authentication aborted."}), content_type='application/json')
    key = RSA.construct((long(account.N), long(account.e), long(account.d)))
    user_cipher = PKCS1_OAEP.new(key)
    token = user_cipher.decrypt(b16decode(encrypted_token))
    pinyto_cipher = PKCS1_OAEP.new(PINYTO_PUBLICKEY)
    authentication_token = b16encode(pinyto_cipher.encrypt(token))
    return HttpResponse(json.dumps({'token': authentication_token}), content_type='application/json')


def register(request):
    """
    Register a new account at the keyserver.

    @param request:
    @return:
    """
    name = request.POST['name']
    password = request.POST['password']
    if Account.objects.filter(name=name).count() > 0:
        return HttpResponse(
            json.dumps({'error': "The requested username is already taken. Registration failed."}),
            content_type='application/json')
    new_account = Account.create(name, password)
    # Register at the PinytoCloud
    key_data = {'N': unicode(new_account.N), 'e': unicode(new_account.e)}
    response = cloud_register(name, key_data)
    if not 'success' in response or not response['success']:
        new_account.delete()
        return HttpResponse(
            json.dumps(
                {'error': "Registration failed. The Pinyto-Cloud responded with a failure: " + response['error']}
            ), content_type='application/json')
    else:
        return HttpResponse(json.dumps({'success': True}), content_type='application/json')


def change_password(request):
    """
    Change the password of the account specified by the token.

    @param request: Django request
    @return: json response
    """
    session = check_token(request.POST.get('token'))
    # check_token will return an error response if the token is not found or can not be verified.
    if isinstance(session, Session):
        if not 'password' in request.POST:
            return HttpResponse(
                json.dumps(
                    {'error': "You have to supply a password if you want to set one."}
                ), content_type='application/json')
        Account.objects.get(name=session.user.name).change_password(request.POST['password'])
        return HttpResponse(json.dumps({'success': True}), content_type='application/json')
    else:
        # session is not a session so it has to be response object with an error message
        return session