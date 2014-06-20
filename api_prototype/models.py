# coding=utf-8
"""
This File is part of Pinyto
"""

from api_prototype.sandbox_helpers import write_to_pipe, read_from_pipe, piped_command


class SandboxCollectionWrapper(object):
    """
    This wrapper is user to expose the db to the users assemblies.
    This is the class with the same methods to be used in the sandbox.
    """

    def __init__(self, child_pipe):
        self.child = child_pipe

    def find(self, query, limit=0):
        """
        Use this function to read from the database. This method
        encodes all fields beginning with _ for returning a valid
        json response.

        @param query: json string
        @param limit: int
        @return: dict
        """
        return piped_command(self.child, {'db.find': {'query': query, 'limit': limit}})

    def count(self, query):
        """
        Use this function to get a count from the database.

        @param query: json string
        @return: dict
        """
        return int(piped_command(self.child, {'db.count': {'query': query}}))

    def find_documents(self, query, limit=0):
        """
        Use this function to read from the database. This method
        returns complete documents with _id fields. Do not use this
        to construct json responses!

        @param query: json string
        @param limit: integer
        @return: dict
        """
        return piped_command(self.child, {'db.find_documents': {'query': query, 'limit': limit}})

    def find_document_for_id(self, document_id):
        """
        Find the document with the given ID in the database. On
        success this returns a single document.

        @param document_id: string
        @return: dict
        """
        return piped_command(self.child, {'db.find_document_for_id': {'document_id': document_id}})

    def save(self, document):
        """
        Saves the document. The document must have a valid _id

        @param document:
        @return:
        """
        return piped_command(self.child, {'db.save': {'document': document}})

    def insert(self, document):
        """
        Inserts a document. If the given document has a ID the
        ID is removed and a new ID will be generated. Time will
        be set to now.

        @param document:
        @return:
        """
        return piped_command(self.child, {'db.insert': {'document': document}})

    def remove(self, document):
        """
        Deletes the document. The document must have a valid _id

        @param document:
        @return:
        """
        return piped_command(self.child, {'db.remove': {'document': document}})
