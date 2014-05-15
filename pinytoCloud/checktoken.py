# coding=utf-8
"""
This File is part of Pinyto
"""

from pinytoCloud.models import Session
from service.response import json_response
import logging


# Get an instance of a logger
logger = logging.getLogger(__name__)


def check_token(token, signature):
    """
    Checks the signature and the token. If all is ok the session is returned.

    @param token: string
    @param signature: long
    @return: Session
    """
    try:
        session = Session.objects.filter(token=token).all()[0]
    except IndexError:
        return json_response({'error': "Unknown token. Please authenticate."})
    if not session.key.get_key().verify(token, (long(signature),)):
        logger.warning("Wrong signature on a request on " + session.token)
        return json_response(
            {'error': "The token was found but the signature did not match. This incident was reported."}
        )
    return session