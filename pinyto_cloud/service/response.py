from django.http import HttpResponse
import json


def json_response(data):
    return HttpResponse(json.dumps(data), mimetype='application/json')