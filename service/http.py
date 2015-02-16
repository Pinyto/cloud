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
