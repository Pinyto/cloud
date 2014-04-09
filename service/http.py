# coding=utf-8
"""
This File is part of Pinyto
"""

from httplib import HTTPSConnection


def secure_request(domain, path, request_type='GET'):
    """
    This issues a http request to the supplied url ant returns
    the response as a string. If the request fails an empty
    string is returned.

    @param domain: string
    @param path: string
    @param request_type: 'GET' or 'POST'
    @return: string
    """
    connection = HTTPSConnection(domain)
    connection.request(request_type, path)
    response = connection.getresponse()
    if response.status != 200:
        connection.close()
        return ""
    content = response.read()
    connection.close()
    return content
