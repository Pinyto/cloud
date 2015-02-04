# coding=utf-8
"""
This File is part of Pinyto
"""

import requests
from requests.exceptions import RequestException, ConnectionError, HTTPError


class Http():
    """
    Objects of this class can be used to connect to remote websites.
    """
    def __init__(self):
        pass

    @staticmethod
    def get(url):
        """
        This issues a http request to the supplied url and returns
        the response as a string. If the request fails an empty
        string is returned.

        :param url: Url with http:// or https:// at the beginning
        :type: str
        :rtype: str
        """
        try:
            response = requests.get(url)
        except RequestException or ConnectionError or HTTPError:
            return ""
        if response.status_code != requests.codes.ok:
            return ""
        return response.text

    @staticmethod
    def post(url="", data=None):
        """
        This issues a http request to the supplied url and returns
        the response as a string. If the request fails an empty
        string is returned.

        For the params do not forget to add an @ to the beginning of each param name.

        :param url: Url with http:// or https:// at the beginning
        :type url: str
        :param data: payload data
        :type data: dict
        :rtype: str
        """
        try:
            response = requests.post(url, data=data)
        except RequestException or ConnectionError or HTTPError:
            return ""
        if response.status_code != requests.codes.ok:
            return ""
        return response.text
