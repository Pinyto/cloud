# coding=utf-8
"""
This File is part of Pinyto
"""

from Crypto.Cipher import PKCS1_OAEP
from pinytoCloud.settings import PINYTO_KEY
from base64 import b16decode
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
    cipher = PKCS1_OAEP.new(PINYTO_KEY)
    if type(encrypted_token) != str:
        encrypted_token = str(encrypted_token)
    try:
        decoded_token = b16decode(encrypted_token)
    except binascii.Error:
        return json_response({'error': "The token is not in valid base16-format."})
    try:
        token = cipher.decrypt(decoded_token)
    except ValueError:
        return json_response({'error': "The token has an invalid length."})
    try:
        session = Session.objects.filter(token=token).all()[0]
    except IndexError:
        return json_response({'error': "Unknown token. Please authenticate."})
    return session