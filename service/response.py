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

from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.http import HttpResponseNotFound, HttpResponseServerError
import json


def json_response(data):
    """
    Returns the json as string with correct mimetype.

    @param data: dict
    @return: HttpResponse
    """
    return HttpResponse(json.dumps(data), content_type='application/json')


def json_bad_request_response(data):
    """
    Returns the json as string with correct mimetype.

    @param data: dict
    @return: HttpResponse
    """
    return HttpResponseBadRequest(json.dumps(data), content_type='application/json')


def json_forbidden_response(data):
    """
    Returns the json as string with correct mimetype.

    @param data: dict
    @return: HttpResponse
    """
    return HttpResponseForbidden(json.dumps(data), content_type='application/json')


def json_not_found_response(data):
    """
    Returns the json as string with correct mimetype.

    @param data: dict
    @return: HttpResponse
    """
    return HttpResponseBadRequest(json.dumps(data), content_type='application/json')


def json_server_error_response(data):
    """
    Returns the json as string with correct mimetype.

    @param data: dict
    @return: HttpResponse
    """
    return HttpResponseServerError(json.dumps(data), content_type='application/json')
