# coding=utf-8
"""
This File is part of Pinyto
"""
from pymongo import MongoClient  # hmm
from service.database import remove_underscore_fields_list


class PinytoAPI(object):
    """
    This is the Prototype for all views. If a request is processed
    all API-Classes (which are children of this one) get called in
    the order of their importance. If a view returns False the next
    Class is called. If one view returns json the chain completes.
    """

    def __init__(self):
        self.db = MongoClient().pinyto.data  # hmm
        self.complete()

    def find(self, query):
        """
        Use this function to read from the database.

        @param query:
        @return: dict
        """
        return remove_underscore_fields_list(self.db.find(query))

    @staticmethod
    def compress():
        """
        This function is called if the available space should be used
        more efficiently. You should implement this method if the data
        for this use case can be compressed. Compression could mean
        that results are stored and raw data gets deleted.

        @return: boolean (True if the data got compressed)
        """
        return False

    @staticmethod
    def complete():
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