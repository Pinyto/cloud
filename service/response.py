from django.http import HttpResponse
import json


def json_response(data):
    """
    Returns the json as string with correct mimetype.

    @param data: dict
    @return: HttpResponse
    """
    return HttpResponse(json.dumps(data), content_type='application/json')