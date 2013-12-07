# coding=utf-8
"""
This File is part of Pinyto
"""

from api_prototype.views import PinytoAPI
from service.response import *
from httplib import HTTPSConnection
from bs4 import BeautifulSoup, NavigableString


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

    def extract_content(self, tag):
        """
        Takes a tag and returns the string content without markup.

        @param tag: BeautifulSoup Tag
        @return: string
        """
        content = u''
        for c in tag.contents:
            if not isinstance(c, NavigableString):
                content += self.extract_content(c)
            content += unicode(c)
        for child in tag.findAll(True):
            for c in child.contents:
                if not isinstance(c, NavigableString):
                    content += self.extract_content(c)
                content += unicode(c)
        return u' '.join(content.split())

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
        print('::Anzahl: ' + str(len(incomplete_books)))
        for book in incomplete_books:
            query = ''
            if 'ean' in book:
                query = book['ean']
            if 'isbn' in book:
                query = book['isbn']
            connection = HTTPSConnection('portal.dnb.de')
            connection.request('GET', '/opac.htm?query=' + query + '&method=simpleSearch')
            response = connection.getresponse()
            content = response.read()
            soup = BeautifulSoup(content)
            table = soup.find('table', attrs={'summary': "Vollanzeige des Suchergebnises"})  # They have a typo here!
            for tr in table.findAll('tr'):
                field_name = ''
                for td in tr.findAll('td', recursive=False):
                    # set Author
                    if not 'author' in book:
                        if field_name == u'Person(en)':
                            book['author'] = self.extract_content(td)
                    # set Title
                    if not 'title' in book:
                        if field_name == u'Mehrteiliges Werk':
                            book['title'] = self.extract_content(td)
                        if field_name == u'Titel':
                            book['title'] = self.extract_content(td)
                    # set Uniform Title
                    if not 'uniform_title' in book:
                        if field_name == u'Einheitssachtitel':
                            book['uniform_title'] = self.extract_content(td)
                    # set Year
                    if not 'year' in book:
                        if field_name == u'Zugehörige Bände':
                            years = []
                            for volume_tag in td.findAll('li'):
                                volume_infos = self.extract_content(volume_tag).split('<br/>')
                                try:
                                    years.append(int(volume_infos[-1]))
                                except ValueError:
                                    pass
                            if len(years) > 0:
                                year = years[0]
                                years_are_the_same = True
                                for check_year in years:
                                    if year != check_year:
                                        years_are_the_same = False
                                if years_are_the_same:
                                    book['year'] = year
                        if field_name == u'Erscheinungsjahr':
                            try:
                                book['year'] = int(self.extract_content(td))
                            except ValueError:
                                pass
                    # set Languages
                    if not 'languages' in book:
                        if field_name == u'Sprache(n)':
                            book['languages'] = self.extract_content(td)
                    # set Category
                    if not 'category' in book:
                        if field_name == u'Sachgruppe(n)':
                            book['category'] = self.extract_content(td)
                    # set Publisher
                    if not 'publisher' in book:
                        if field_name == u'Verleger':
                            book['publisher'] = self.extract_content(td)
                    # set Edition
                    if not 'edition' in book:
                        if field_name == u'Ausgabe':
                            book['edition'] = self.extract_content(td)
                    # set ISBN
                    if not 'isbn' in book:
                        if field_name == u'ISBN/Einband/Preis':
                            isbn, more = self.extract_content(td).split(' ', 1)
                            book['isbn'] = isbn
                    # set EAN
                    if not 'ean' in book:
                        if field_name == u'EAN':
                            book['ean'] = self.extract_content(td)
                    # find label
                    name_tag = td.find('strong')
                    if name_tag:
                        field_name = name_tag.string

            print('_____________')
            print(book)
            connection.close()
        return False