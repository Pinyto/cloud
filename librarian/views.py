# coding=utf-8
"""
This File is part of Pinyto
"""

from api_prototype.views import PinytoAPI
from service.response import *
from httplib import HTTPSConnection
from bs4 import BeautifulSoup


class Librarian(PinytoAPI):
    """
    This class is used for managing books.
    """

    def view(self, request):
        """
        Public View

        @param request:
        @return: json
        """
        print("Library lookup.")
        request_type = request.GET.get('type')
        print(request_type)
        if request_type == 'index':
            ean = request.GET.get('ean')
            isbn = request.GET.get('isbn')
            if ean:
                books = self.find({'type': 'book', 'ean': ean})
            elif isbn:
                books = self.find({'type': 'book', 'isbn': isbn})
            else:
                books = self.find({'type': 'book'})
            print(books)
            return json_response({'index': books})
        elif request_type == 'search':
            search_string = request.GET.get('searchstring')
            print('Serching for: ' + search_string)
            books = self.find({'type': 'book',
                               '$or': [
                                   {'title': {'$regex': search_string, '$options': 'i'}},
                                   {'description': {'$regex': search_string, '$options': 'i'}}
                               ]})
            return json_response({'index': books})
        else:
            print("wrong Type")
            return False

    def complete(self):
        """
        Tries to load missing data from the german national library website.

        @return: boolean
        """
        incomplete_books = self.find({'type': 'book',
                                      '$or': [
                                          {'title': {'$exists': False}},
                                          {'description': {'$exists': False}}
                                      ]})
        for book in incomplete_books:
            query = ''
            if book['ean']:
                query = book['ean']
            if book['isbn']:
                query = book['isbn']
            connection = HTTPSConnection('portal.dnb.de/opac.htm?query='+query+'&method=simpleSearch')
            response = connection.read()
            print(response)
            soup = BeautifulSoup(response)
        return False