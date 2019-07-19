# -*- coding: utf-8 -*-
"""
Pinyto cloud - A secure cloud database for your personal data
Copyright (C) 2019 Pina Merkert <pina@pinae.net>

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
import json


class BodyFat:
    """
    This is the assembly for the Caliper app.
    """

    @staticmethod
    def load_fat_history(request, db, factory):
        """
        Returns a list of all body fat readings sorted by saved date.

        @param request: Django Request
        @param db: DatabaseWrapper
        @param factory: Factory (either service.models.Factory or api_prototype.models.Factory)
        @return: string
        """
        return {'result': db.find(
            query={'type': 'body_fat'},
            skip=0,
            limit=10000,
            sorting='data.date',
            sort_direction='asc')}

    @staticmethod
    def save(request, db, factory):
        """
        save inserts or updates the given body fat reading depending on the document having an existing id or not.
        If it has a _id field but the id does not exist the field will be removed and the saved document gets a
        new id from the database.
        The assigned _id is returned which indicates that the document was successfully saved.

        @param request: Django Request
        @param db: DatabaseWrapper
        @param factory: Factory (either service.models.Factory or api_prototype.models.Factory)
        @return: string
        """
        try:
            request_data = json.loads(str(request.body, encoding='utf-8'))
        except ValueError:
            return {'error': 'The request needs to be in JSON format. This was not JSON.'}
        if 'document' not in request_data:
            return {'error': 'You have to supply a document to save.'}
        document = request_data['document']
        if not isinstance(document, dict):
            return {'error': 'The document you supplied is not a single document. ' +
                             'Only one document at a time will be saved.'}
        if 'type' not in document or document['type'] != 'body_fat':
            return {'error': 'The document you sent is not of type body_fat. ' +
                             'This function only saves body_fat readings.'}
        if not ('_id' in document and db.count({'_id': document['_id']}) > 0):
            str_id = db.insert(document)
        else:
            str_id = db.save(document)
        return {'success': True, '_id': str_id}

    @staticmethod
    def delete(request, db, factory):
        """
        remove removes the fat reading specified by the _id.

        @param request: Django Request
        @param db: DatabaseWrapper
        @param factory: Factory (either service.models.Factory or api_prototype.models.Factory)
        @return: string
        """
        try:
            request_data = json.loads(str(request.body, encoding='utf-8'))
        except ValueError:
            return {'error': 'The request needs to be in JSON format. This was not JSON.'}
        if 'document' not in request_data:
            return {'error': 'You have to supply a document to delete.'}
        document = request_data['document']
        if '_id' not in document:
            return {'error': 'You have to specify an _id to identify the body_fat document you want to delete.'}
        if not db.count({'_id': document['_id'], 'type': 'body_fat'}) > 0:
            return {'error': 'There is no body_fat reading with this ID. The document could not be deleted.'}
        db.remove(document)
        return {'success': True}
