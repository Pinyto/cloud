# coding=utf-8
"""
This File is part of Pinyto
"""

import json
import struct

from api_prototype.sandbox_helpers import write_to_pipe


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
        write_to_pipe(self.child, {'db.find': {'query': query, 'limit': limit}})

    def ping(self):
        write_to_pipe(self.child, {'db.ping': True})