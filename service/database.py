# coding=utf-8
"""
This File is part of Pinyto
"""

from pymongo.son_manipulator import ObjectId
from pymongo import ASCENDING, DESCENDING
from datetime import datetime


class CollectionWrapper(object):
    """
    This wrapper is user to expose the db to the users assemblies.
    """
    def __init__(self, collection):
        self.db = collection

    def find(self, query, skip=0, limit=0, sorting=None, sort_direction='asc'):
        """
        Use this function to read from the database. This method
        encodes all fields beginning with _ for returning a valid
        json response.

        @param query: json string
        @param skip: integer
        @param limit: int
        @param sorting: string identifiying the key
        @param sort_direction: 'asc' or 'desc'
        @return: dict
        """
        return encode_underscore_fields_list(self.find_documents(
            inject_object_id(query),
            skip=skip,
            limit=limit,
            sorting=sorting,
            sort_direction=sort_direction
        ))

    def count(self, query):
        """
        Use this function to get a count from the database.

        @param query: json string
        @return: dict
        """
        return self.db.find(inject_object_id(query)).count()

    def find_documents(self, query, skip=0, limit=0, sorting=None, sort_direction='asc'):
        """
        Use this function to read from the database. This method
        returns complete documents with _id fields. Do not use this
        to construct json responses!

        @param query: json string
        @param skip: integer
        @param limit: integer
        @param sorting: string identifiying the key
        @param sort_direction: 'asc' or 'desc'
        @return: dict
        """
        if sort_direction == 'desc':
            sort_direction = DESCENDING
        else:
            sort_direction = ASCENDING
        if sorting:
            return self.db.find(inject_object_id(query), skip=skip, limit=limit, sort=[(sorting, sort_direction)])
        else:
            return self.db.find(inject_object_id(query), skip=skip, limit=limit)

    def find_document_for_id(self, document_id):
        """
        Find the document with the given ID in the database. On
        success this returns a single document.

        @param document_id: string
        @return: dict
        """
        return self.db.find_one(inject_object_id({'_id': document_id}))

    def find_distinct(self, query, attribute):
        """
        Return a list representing the diversity of a given attribute in
        the documents matched by the query.

        @param query: json string
        @param attribute: string
        @return:
        """
        return self.db.find(inject_object_id(query)).distinct(attribute)

    def save(self, document):
        """
        Saves the document. The document must have a valid _id

        @param document:
        @return:
        """
        if not isinstance(document['_id'], ObjectId):
            document['_id'] = ObjectId(document['_id'])
        return str(self.db.save(document))

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
        return str(self.db.insert(document))

    def remove(self, document):
        """
        Deletes the document. The document must have a valid _id

        @param document:
        @return:
        """
        self.db.remove(spec_or_id=inject_object_id({"_id": document['_id']}))


def encode_underscore_fields(data):
    """
    Removes _id

    @param data: dict
    @return: dict
    """
    converted = {}
    for key in data:
        if key[0] != '_':
            if key == 'time':
                converted[key] = str(data[key])
            else:
                converted[key] = data[key]
        else:
            converted[key] = str(data[key])
    return converted


def encode_underscore_fields_list(data_list):
    """
    Removes _id for every dict in the list

    @param data_list: [dict]
    @return: [dict]
    """
    converted_list = []
    for item in data_list:
        converted_list.append(encode_underscore_fields(item))
    return converted_list


def inject_object_id(query):
    """
    Traverses all fields of the query dict and converts all '_id' to ObjectId instances.

    @param query: dict
    @return: dict
    """
    if isinstance(query, list):
        for index, value in enumerate(query):
            if isinstance(value, dict) or isinstance(value, list):
                query[index] = inject_object_id(value)
    else:
        for key in query:
            if key == '_id' and not isinstance(query[key], ObjectId):
                query[key] = ObjectId(query[key])
            if isinstance(query[key], dict) or isinstance(query[key], list):
                query[key] = inject_object_id(query[key])
    return query