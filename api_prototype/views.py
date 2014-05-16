# coding=utf-8
"""
This File is part of Pinyto
"""
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.son_manipulator import ObjectId
from service.database import encode_underscore_fields_list
from service.response import json_response
from pinytoCloud.checktoken import check_token
from pinytoCloud.models import Session
from datetime import datetime

ApiClasses = [('librarian.views', 'Librarian')]


def load(request):
    """
    If a request is processed
    all API-Classes get called in the order specified in ApiClasses.
    If a view returns False the next Class is called. If one view
    returns json the chain completes.

    @param request:
    @return: json
    """
    session = check_token(request.POST.get('token'))
    # check_token will return an error response if the token is not found or can not be verified.
    if isinstance(session, Session):
        for api_class_origin, api_class_name in ApiClasses:
            module = __import__(api_class_origin, globals(), locals(), api_class_name)
            api_object = getattr(module, api_class_name)(session.user.name)
            result = api_object.view(request)
            if result:
                return result
        return json_response(
            {'error': "The type of your request didn't match a known type. Please use one of [index] or no type."})
    else:
        # session is not a session so it has to be response object with an error message
        return session


class PinytoAPI(object):
    """
    This is the Prototype for all views. If a request is processed
    all API-Classes (which are children of this one) get called in
    the order of their importance. If a view returns False the next
    Class is called. If one view returns json the chain completes.
    """

    def __init__(self, username):
        self.db = Collection(MongoClient().pinyto, username)

    def find(self, query, limit=0):
        """
        Use this function to read from the database. This method
        encodes all fields beginning with _ for returning a valid
        json response.

        @param query: json string
        @param limit: int
        @return: dict
        """
        return encode_underscore_fields_list(self.db.find(query).limit(limit))

    def count(self, query):
        """
        Use this function to get a count from the database.

        @param query: json string
        @return: dict
        """
        return self.db.find(query).count()

    def find_documents(self, query, limit=0):
        """
        Use this function to read from the database. This method
        returns complete documents with _id fields. Do not use this
        to construct json responses!

        @param query:
        @return: dict
        """
        return self.db.find(query).limit(limit)

    def find_document_for_id(self, id):
        """
        Find the document with the given ID in the database. On
        success this returns a single document.

        @param id: string
        @return: dict
        """
        return self.db.find_one({'_id': ObjectId(id)})

    def save(self, document):
        """
        Saves the document. The document must have a valid _id

        @param document:
        @return:
        """
        self.db.save(document)

    def insert(self, document):
        """
        Inserts a document. If the given document has a ID the
        ID is removed and a new ID will be generated. Time will
        be set to now.

        @param document:
        @return:
        """
        if '_id' in document:
            del document['_id']
        document['time'] = datetime.utcnow()
        self.db.insert(document)

    def remove(self, document):
        """
        Deletes the document. The document must have a valid _id

        @param document:
        @return:
        """
        self.db.remove(document['_id'])

    def compress(self):
        """
        This function is called if the available space should be used
        more efficiently. You should implement this method if the data
        for this use case can be compressed. Compression could mean
        that results are stored and raw data gets deleted.

        @return: boolean (True if the data got compressed)
        """
        return False

    def complete(self):
        """
        This function gets called when incomplete data needs to get
        completed. This type of data completion needs to be automatic
        because at this point you will be unable to ask the user for
        more specific data. If you need the latter use data validation
        in the frontend.

        @return: boolean (True if the data was completed, False if
        the completion should be tried later on)
        """
        return True

    def view(self, request):
        """
        Implement this function to create your API. This function gets
        called if a request is processed. Please make sure your view
        returns False if the request did not match your logic.

        @param request:
        @return: json
        """
        raise NotImplementedError("Please Implement this method")
