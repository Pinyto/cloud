# coding=utf-8
"""
This File is part of Pinyto
"""

import json


class DocumentsAdmin():
    """
    This is the admin assembly for editing all documents in the db.
    """
    def __init__(self):
        pass

    @staticmethod
    def search(request, db, factory):
        """
        search accepts a query parameter which must be valid json, a skip value and a count. If search is omitted
        all documents are returned. If skip is omitted no documents will be skipped. If count is omitted 42 documents
        are returned.

        @param request: Django Request
        @param db: DatabaseWrapper
        @param factory: Factory (either service.models.Factory or api_prototype.models.Factory)
        @return: string
        """
        try:
            skip = int(request.POST.get('skip', 0))
        except ValueError:
            return json.dumps({'error': 'The skip value you supplied is not a number.'})
        try:
            count = int(request.POST.get('count', 42))
        except ValueError:
            return json.dumps({'error': 'The count you supplied is not a number.'})
        try:
            query = json.loads(request.Post.get('query', '{}'))
        except ValueError:
            return json.dumps({'error': 'The search param is not in valid JSON format.'})
        return json.dumps({'result': db.find(query=query, skip=skip, count=count)})

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
        if not 'document' in request.POST:
            return json.dumps({'error': 'You have to supply a document to save.'})
        try:
            document = json.loads(request.POST.get('document'))
        except ValueError:
            return json.dumps({'error': 'The document you supplied is not in valid JSON format.'})
        if not isinstance(document, dict):
            return json.dumps({'error': 'The document you supplied is not a single document. ' +
                                        'Only one document at a time will be saved.'})
        if not ('_id' in document and db.count({'_id': document['_id']}) > 0):
            str_id = db.insert(document)
            document['_id'] = str_id
        db.save(document)
        return json.dumps({'success': True, '_id': document['_id']})

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
            document = json.loads(request.POST['document'])
        except IndexError:
            return json.dumps({'error': 'You have to supply a document to delete.'})
        except ValueError:
            return json.dumps({'error': 'The document you supplied is not valid json.'})
        if not '_id' in document:
            return json.dumps({'error': 'You have to specify an _id to identify the document you want to delete.'})
        if not db.count({'_id': document['_id']}) > 0:
            return json.dumps({'error': 'There is no document with this ID. The document could not be deleted.'})
        db.remove(document)
        return json.dumps({'success': True})