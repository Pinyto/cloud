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

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from pinytoCloud.settings import PINYTO_KEY
from base64 import b64decode
from pinytoCloud.models import Session
from service.response import json_response
import logging
import binascii


# Get an instance of a logger
logger = logging.getLogger(__name__)


def check_token(encrypted_token):
    """
    Decrypts the token and finds the matching session.
    If an error occurs this will return an error response.
    If all is ok the session is returned.

    @param encrypted_token: string
    @return: Session
    """
    if type(encrypted_token) != str:
        encrypted_token = str(encrypted_token)
    try:
        decoded_token = b64decode(encrypted_token.encode('utf-8'))
    except binascii.Error:
        return json_response({'error': "The token is not in valid base64-format."})
    try:
        token = PINYTO_KEY.decrypt(
            decoded_token,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA1()),
                algorithm=hashes.SHA1(),
                label=None)
        )
    except ValueError as e:
        return json_response({'error': "The token could not be decoded: " + str(e)})
    except AssertionError as e:
        return json_response({'error': "During decryption of the token an error occurred: " + str(e)})
    try:
        session = Session.objects.filter(token=token).all()[0]
    except IndexError:
        return json_response({'error': "Unknown token. Please authenticate."})
    return session