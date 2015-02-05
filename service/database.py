# coding=utf-8
"""
This File is part of Pinyto
"""

from pymongo.son_manipulator import ObjectId
from pymongo.errors import InvalidId
from pymongo import ASCENDING, DESCENDING
from datetime import datetime


class CollectionWrapper(object):
    """
    This wrapper is user to expose the db to the users assemblies.
    """
    def __init__(self, collection, assembly_name, only_own_data=True):
        self.db = collection
        self.assembly_name = assembly_name
        self.only_own_data = only_own_data

    def find(self, query, skip=0, limit=0, sorting=None, sort_direction='asc'):
        """
        Use this function to read from the database. This method
        encodes all fields beginning with _ for returning a valid
        json response.

        :param query:
        :type query: dict
        :param skip: Count of documents which should be skipped in the query. This is useful for pagination.
        :type skip: int
        :param limit: Number of documents which should be returned. This number is of course the maximum.
        :type limit: int
        :param sorting: String identifying the key which is used for sorting.
        :type sorting: str
        :param sort_direction: 'asc' or 'desc'
        :type sort_direction: str
        :return: The list of found documents. If no document is found the list is empty.
        :rtype: list
        """
        if self.only_own_data:
            query['assembly'] = self.assembly_name
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

        :param query:
        :type query: dict
        :return: The number of documents matching the query
        :rtype: int
        """
        if self.only_own_data:
            query['assembly'] = self.assembly_name
        try:
            count = self.db.find(inject_object_id(query)).count()
        except InvalidId:
            count = -1
        return count

    def find_documents(self, query, skip=0, limit=0, sorting=None, sort_direction='asc'):
        """
        Use this function to read from the database. This method
        returns complete documents with _id fields. Do not use this
        to construct json responses!

        :param query:
        :type query: dict
        :param skip: Count of documents which should be skipped in the query. This is useful for pagination.
        :type skip: int
        :param limit: Number of documents which should be returned. This number is of course the maximum.
        :type limit: int
        :param sorting: String identifying the key which is used for sorting.
        :type sorting: str
        :param sort_direction: 'asc' or 'desc'
        :type sort_direction: str
        :return: The list of found documents. If no document is found the list is empty.
        :rtype: list
        """
        if self.only_own_data:
            query['assembly'] = self.assembly_name
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

        :param document_id:
        :type document_id: string
        :return: The document with the given _id
        :rtype: dict
        """
        if self.only_own_data:
            return self.db.find_one(inject_object_id({'_id': document_id, 'assembly': self.assembly_name}))
        else:
            return self.db.find_one(inject_object_id({'_id': document_id}))

    def find_distinct(self, query, attribute):
        """
        Return a list representing the diversity of a given attribute in
        the documents matched by the query.

        :param query: json
        :type query: str
        :param attribute: String describing the attribute
        :type attribute: str
        :return: A list of values the attribute can have in the set of documents described by the query
        :rtype: list
        """
        if self.only_own_data:
            query['assembly'] = self.assembly_name
        return self.db.find(inject_object_id(query)).distinct(attribute)

    def save(self, document):
        """
        Saves the document. The document must have a valid _id

        :param document:
        :type document: dict
        :return: The ObjectId of the insrted document
        :rtype: str
        """
        document['assembly'] = self.assembly_name
        if not isinstance(document['_id'], ObjectId):
            document['_id'] = ObjectId(document['_id'])
        return str(self.db.save(document))

    def insert(self, document):
        """
        Inserts a document. If the given document has a ID the
        ID is removed and a new ID will be generated. Time will
        be set to now.

        :param document:
        :type document: dict
        :return: The ObjectId of the insrted document
        :rtype: str
        """
        if '_id' in document:
            del document['_id']
        document['time'] = datetime.utcnow()
        document['assembly'] = self.assembly_name
        return str(self.db.insert(document))

    def remove(self, document):
        """
        Deletes the document. The document must have a valid _id

        :param document:
        :type document: dict
        """
        if self.only_own_data:
            self.db.remove(spec_or_id=inject_object_id({"_id": document['_id'], 'assembly': self.assembly_name}))
        else:
            self.db.remove(spec_or_id=inject_object_id({"_id": document['_id']}))


def encode_underscore_fields(data):
    """
    Removes _id

    :param data:
    :type data: dict
    :rtype: dict
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

    :param data_list:
    :type data_list: list
    :rtype: list
    """
    converted_list = []
    for item in data_list:
        converted_list.append(encode_underscore_fields(item))
    return converted_list


def inject_object_id(query):
    """
    Traverses all fields of the query dict and converts all '_id' to ObjectId instances.

    :param query:
    :type query: dict
    :rtype: dict
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