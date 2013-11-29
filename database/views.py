# coding=utf-8
"""
This File is part of Pinyto
"""
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from project_path import project_path
from pymongo import MongoClient
from service.response import json_response
from datetime import datetime


def home(request):
    """
    This should not be necessary.
    @param request:
    @return:
    """
    with open(project_path("static/index.html"), 'r') as index_html_file:
        return HttpResponse(index_html_file.read(), mimetype='text/html')


@csrf_exempt
def store(request):
    """
    Store document in any format. The date of creation and request.user will be
    added automatically to the document

    :param request:
    """
    print("Store!")
    data = request.POST.get('data')
    data_type = request.POST.get('type')
    if data and data_type:
        db = MongoClient().pinyto.data
        document = {'type': data_type,
                    'time': datetime.utcnow(),
                    'data': data}
        db.insert(document)
        return json_response({'success': True})
    else:
        return json_response({'error': "If you want to store data you have to send your " +
                                       "data as json string in a POST request in the parameter 'data'. " +
                                       "You also have to supply a type string for the data."})