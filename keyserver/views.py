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

from keyserver.models import Account
from hashlib import sha256
import json
from base64 import b64encode, b64decode
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from keyserver.settings import PINYTO_PUBLIC_KEY
from pinytoCloud.views import authenticate as cloud_authenticate
from pinytoCloud.views import register as cloud_register
from pinytoCloud.checktoken import check_token, PinytoTokenError
from service.response import json_response, json_bad_request_response
from service.response import json_not_found_response, json_forbidden_response, json_server_error_response


def authenticate(request):
    """
    Authenticate at the keyserver.

    :param request: Django request
    :type request: HttpRequest
    :return: json response
    :rtype: HttpResponse
    """
    try:
        request_data = json.loads(str(request.body, encoding='utf-8'))
    except ValueError:
        return json_bad_request_response(
            {'error': "Please supply username and password as JSON data. " +
                      "This is not valid JSON. Authentication failed."})
    if 'name' not in request_data or 'password' not in request_data:
        return json_bad_request_response(
                {'error': "Please supply username and password in the " +
                          "JSON request data. Authentication failed."})
    name = request_data['name']
    password = request_data['password']
    try:
        account = Account.objects.filter(name=name).all()[0]
    except IndexError:
        return json_not_found_response(
            {'error': name + " is not a valid account name. Authentication failed."})
    if not account.check_password(password):
        return json_forbidden_response(
            {'error': "Wrong password. Authentication failed."})
    # Make a request to Pinyto-Cloud asking for a encrypted token
    hasher = sha256()
    hasher.update((account.N + str(account.e)).encode('utf-8'))
    response = cloud_authenticate(name, hasher.hexdigest()[:10])
    if 'error' in response:
        return json_server_error_response(
            {'error': "Cloud Error: " + response['error'] + " Authentication failed."})
    if 'encrypted_token' not in response or 'signature' not in response:
        return json_bad_request_response(
            {'error': "Malformatted Response of the Pinyto-Cloud. Authentication failed."})
    encrypted_token = response['encrypted_token']
    signature = b64decode(response['signature'].encode('utf-8'))
    try:
        PINYTO_PUBLIC_KEY.verify(
            signature,
            encrypted_token.encode('utf-8'),
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )
    except InvalidSignature:
        return json_forbidden_response(
            {'error': "Pinyto-Cloud signature is wrong. This is a man-in-the-middle-attack! " +
                      "The developers will be informed. Authentication aborted."})
    public_numbers = rsa.RSAPublicNumbers(account.e, int(account.N))
    p = int(account.p)
    q = int(account.q)
    d = int(account.d)
    dmp1 = rsa.rsa_crt_dmp1(account.e, p)
    dmq1 = rsa.rsa_crt_dmq1(account.e, q)
    iqmp = rsa.rsa_crt_iqmp(p, q)
    key = rsa.RSAPrivateNumbers(p, q, d, dmp1, dmq1, iqmp, public_numbers).private_key(default_backend())
    token = key.decrypt(
        b64decode(encrypted_token.encode('utf-8')),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA1()),
            algorithm=hashes.SHA1(),
            label=None)
    )
    authentication_token = str(b64encode(PINYTO_PUBLIC_KEY.encrypt(
        token,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA1()),
            algorithm=hashes.SHA1(),
            label=None)
    )), encoding='utf-8')
    return json_response({'token': authentication_token})


def register(request):
    """
    Register a new account at the keyserver.

    :param request: Django request
    :type request: HttpRequest
    :return: json response
    :rtype: HttpResponse
    """
    try:
        request_data = json.loads(str(request.body, encoding='utf-8'))
    except ValueError:
        return json_bad_request_response(
            {'error': "Please supply username and password as JSON data. " +
                      "This is not valid JSON. Registration failed."})
    try:
        name = request_data['name']
        password = request_data['password']
    except IndexError:
        return json_bad_request_response(
                {'error': "Please supply username and password in the JSON request data. " +
                          "Registration failed."})
    if Account.objects.filter(name=name).count() > 0:
        return json_bad_request_response(
            {'error': "The requested username is already taken. Registration failed."})
    new_account = Account.create(name, password)
    # Register at the PinytoCloud
    key_data = {'N': str(new_account.N), 'e': str(new_account.e)}
    response = cloud_register(name, key_data)
    if 'success' not in response or not response['success']:
        new_account.delete()
        return json_server_error_response(
                {'error': "Registration failed. The Pinyto-Cloud responded with a failure: " +
                          response['error']})
    else:
        return json_response({'success': True})


def change_password(request):
    """
    Change the password of the account specified by the token.

    :param request: Django request
    :type request: HttpRequest
    :return: json response
    :rtype: HttpResponse
    """
    try:
        request_data = json.loads(str(request.body, encoding='utf-8'))
    except ValueError:
        return json_bad_request_response(
            {'error': "Please supply the new password as JSON data. " +
                      "This is not valid JSON. Password change failed."})
    try:
        token = request_data['token']
        password = request_data['password']
    except IndexError:
        return json_bad_request_response(
                {'error': "Please supply the new password in the JSON " +
                          "request data. Password change failed."})
    try:
        session = check_token(token)
    except PinytoTokenError as e:
        return json_bad_request_response(e.error_json)
    Account.objects.get(name=session.user.name).change_password(password)
    return json_response({'success': True})
