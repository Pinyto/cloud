from django.http import HttpResponse
from project_path import project_path
from pymongo import MongoClient
import json

def home(request):
    with open(project_path("static/index.html"), 'r') as index_html_file:
        return HttpResponse(index_html_file.read(), mimetype='text/html')


def store(request):
    """
    Store document in any format. The date of creation and request.user will be
    added automatically to the document

    :param request:
    """
    db = MongoClient().pinyto
    leute = db.leute.find()
    data = []
    for jemand in leute:
        person = {}
        for key in jemand:
            if key[0] != '_':
                person[key] = jemand[key]
        data.append(person)
    return HttpResponse(json.dumps(data), mimetype='application/json')
    pass