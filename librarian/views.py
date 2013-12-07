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
        if tag.string:
            content += tag.string
        for child in tag.findAll(True):
            content += child.string
        return ' '.join(content.split())

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
            table = soup.find('table', attrs={'summary': "Vollanzeige des Suchergebnises"})  # They have a typo here!
            for tr in table.findAll('tr'):
                field_name = ''
                for td in tr.findAll('td', recursive=False):
                    # set Author
                    if not 'author' in book:
                        if field_name == 'Person(en)':
                            book['author'] = self.extract_content(td)
                    # set Title
                    if not 'title' in book:
                        if field_name == 'Mehrteiliges Werk':
                            book['title'] = self.extract_content(td)
                        if field_name == 'Titel':
                            book['title'] = self.extract_content(td)
                    # set Uniform Title
                    if not 'uniform_title' in book:
                        if field_name == 'Einheitssachtitel':
                            book['uniform_title'] = self.extract_content(td)
                    # set Year
                    if not 'year' in book:
                        if field_name == 'Erscheinungsjahr':
                            book['year'] = self.extract_content(td)
                    # set Languages
                    if not 'languages' in book:
                        if field_name == 'Sprache(n)':
                            book['languages'] = self.extract_content(td)
                    # set Category
                    if not 'category' in book:
                        if field_name == 'Sachgruppe(n)':
                            book['category'] = self.extract_content(td)
                    # set Publisher
                    if not 'publisher' in book:
                        if field_name == 'Verleger':
                            book['publisher'] = self.extract_content(td)
                    # set Edition
                    if not 'edition' in book:
                        if field_name == 'Ausgabe':
                            book['edition'] = self.extract_content(td)
                    # set ISBN
                    if not 'isbn' in book:
                        if field_name == 'ISBN/Einband/Preis':
                            isbn, more = self.extract_content(td).split(' ', 1)
                            book['isbn'] = isbn
                    # set EAN
                    if not 'ean' in book:
                        if field_name == 'EAN':
                            book['ean'] = self.extract_content(td)
                    # find label
                    name_tag = td.find('strong')
                    if name_tag:
                        field_name = name_tag.string

            print('_____________')
            print(book)
            connection.close()
        return False