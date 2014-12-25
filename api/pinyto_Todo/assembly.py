# coding=utf-8
"""
This File is part of Pinyto
"""

import json


class Todo():
    """
    This is the assembly for the Pinyto todo apps.
    """
    def __init__(self):
        pass

    @staticmethod
    def get_list(request, db, factory):
        """
        Returns a list of all todo items sorted by saved date.

        @param request: Django Request
        @param db: DatabaseWrapper
        @param factory: Factory (either service.models.Factory or api_prototype.models.Factory)
        @return: string
        """
        return json.dumps({'result': db.find(
            query={'type': 'todo'},
            skip=0,
            limit=10000,
            sorting='time',
            sort_direction='desc')})

    @staticmethod
    def save(request, db, factory):
        """
        save inserts or updates the given document depending on the document having an existing id or not. If it has a
        _id field but the id does not exist the field will be removed and the saved document gets a new id from the
        database.
        The assigned _id is returned which indicates that the document was successfully saved.

        @param request: Django Request
        @param db: DatabaseWrapper
        @param factory: Factory (either service.models.Factory or api_prototype.models.Factory)
        @return: string
        """
        try:
            request_data = json.loads(request.body)
        except ValueError:
            return json.dumps({'error': 'The request needs to be in JSON format. This was not JSON.'})
        if 'document' not in request_data:
            return json.dumps({'error': 'You have to supply a document to save.'})
        document = request_data['document']
        if not isinstance(document, dict):
            return json.dumps({'error': 'The document you supplied is not a single document. ' +
                                        'Only one document at a time will be saved.'})
        if not ('_id' in document and db.count({'_id': document['_id']}) > 0):
            str_id = db.insert(document)
        else:
            str_id = db.save(document)
        return json.dumps({'success': True, '_id': str_id})

    @staticmethod
    def delete(request, db, factory):
        """
        remove removes the document specified by the _id.

        @param request: Django Request
        @param db: DatabaseWrapper
        @param factory: Factory (either service.models.Factory or api_prototype.models.Factory)
        @return: string
        """
        try:
            request_data = json.loads(request.body)
        except ValueError:
            return json.dumps({'error': 'The request needs to be in JSON format. This was not JSON.'})
        if 'document' not in request_data:
            return json.dumps({'error': 'You have to supply a document to delete.'})
        document = request_data['document']
        if '_id' not in document:
            return json.dumps({'error': 'You have to specify an _id to identify the document you want to delete.'})
        if not db.count({'_id': document['_id']}) > 0:
            return json.dumps({'error': 'There is no document with this ID. The document could not be deleted.'})
        db.remove(document)
        return json.dumps({'success': True})