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

    @staticmethod
    def extract_content(tag):
        """
        Takes a tag and returns the string content without markup.
        @return: string
        """
        content = ''
        for child in tag.findAll(True):
            content += child.string
        return content

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
        print('::Anzahl: '+str(len(incomplete_books)))
        for book in incomplete_books:
            query = ''
            if 'ean' in book:
                query = book['ean']
            if 'isbn' in book:
                query = book['isbn']
            connection = HTTPSConnection('portal.dnb.de')
            connection.request('GET', '/opac.htm?query='+query+'&method=simpleSearch')
            response = connection.getresponse()
            content = response.read()
            soup = BeautifulSoup(content)
            table = soup.find('table')
            for tr in table.findAll('tr'):
                field_name = ''
                for td in tr.findAll('td', recursive=False):
                    if field_name == 'Person(en)':
                        content = self.extract_content(td)
                        print(content)
                    name_tag = td.find('strong')
                    if name_tag:
                        field_name = name_tag.string

            connection.close()
        return False