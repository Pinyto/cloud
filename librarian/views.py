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
                books = self.find({'type': 'book', 'data.ean': ean})
            elif isbn:
                books = self.find({'type': 'book', 'data.isbn': isbn})
            else:
                books = self.find({'type': 'book'})
            print(books)
            return json_response({'index': books})
        elif request_type == 'search':
            search_string = request.GET.get('searchstring')
            print('Serching for: ' + search_string)
            books = self.find({'type': 'book',
                               'data': {'$exists': True},
                               '$or': [
                                   {'data.title': {'$regex': search_string, '$options': 'i'}},
                                   {'data.uniform_title': {'$regex': search_string, '$options': 'i'}},
                                   {'data.publisher': {'$regex': search_string, '$options': 'i'}},
                                   {'data.year': {'$regex': search_string, '$options': 'i'}},
                                   {'data.category': {'$regex': search_string, '$options': 'i'}},
                                   {'data.author': {'$regex': search_string, '$options': 'i'}}
                               ]}, 42)
            return json_response({'index': books})
        elif request_type == 'statistics':
            return json_response({
                'book_count': self.count({'type': 'book'}),
                'places_used': self.find_documents(
                    {'type': 'book', 'data': {'$exists': True}}).distinct('data.place'),
                'lent_count': self.count({'type': 'book',
                                          'data': {'$exists': True},
                                          'data.lent': {'$exists': True, '$ne': ""}})
            })
        else:
            print(request.get_full_path())
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
            else:
                content += unicode(c)
        return u' '.join(content.split())

    def complete(self):
        """
        Tries to load missing data from the german national library website.

        @return: boolean
        """
        incomplete_books = self.find_documents({'type': 'book',
                                                'data': {'$exists': True},
                                                '$or': [
                                                    {'data.author': {'$exists': False}},
                                                    {'data.title': {'$exists': False}},
                                                    {'data.uniform_title': {'$exists': False}},
                                                    {'data.isbn': {'$exists': False}},
                                                    {'data.ean': {'$exists': False}}
                                                ]})
        completion_successful = True
        for book in incomplete_books:
            query = ''
            if 'isbn' in book['data']:
                query = book['data']['isbn']
            if 'ean' in book['data']:
                query = book['data']['ean']
            connection = HTTPSConnection('portal.dnb.de')
            connection.request('GET', '/opac.htm?query=' + query + '&method=simpleSearch')
            response = connection.getresponse()
            if response.status != 200:
                completion_successful = False
                continue
            content = response.read()
            soup = BeautifulSoup(content)
            table = soup.find('table', attrs={'summary': "Vollanzeige des Suchergebnises"})  # They have a typo here!
            if table:
                for tr in table.findAll('tr'):
                    field_name = ''
                    for td in tr.findAll('td', recursive=False):
                        # set Author
                        if not 'author' in book['data']:
                            if field_name == u'Person(en)':
                                book['data']['author'] = self.extract_content(td)

                        # set Title
                        if not 'title' in book['data']:
                            if field_name == u'Mehrteiliges Werk':
                                book['data']['title'] = self.extract_content(td)
                            if field_name == u'Titel':
                                book['data']['title'] = self.extract_content(td)

                        # set Uniform Title
                        if not 'uniform_title' in book['data']:
                            if field_name == u'Einheitssachtitel':
                                book['data']['uniform_title'] = self.extract_content(td)

                        # set Year
                        if not 'year' in book['data']:
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
                                        book['data']['year'] = year
                            if field_name == u'Erscheinungsjahr':
                                try:
                                    book['data']['year'] = int(self.extract_content(td))
                                except ValueError:
                                    pass

                        # set Languages
                        if not 'languages' in book['data']:
                            if field_name == u'Sprache(n)':
                                book['data']['languages'] = self.extract_content(td)

                        # set Category
                        if not 'category' in book['data']:
                            if field_name == u'Sachgruppe(n)':
                                book['data']['category'] = self.extract_content(td)

                        # set Publisher
                        if not 'publisher' in book['data']:
                            if field_name == u'Verleger':
                                book['data']['publisher'] = self.extract_content(td)

                        # set Edition
                        if not 'edition' in book['data']:
                            if field_name == u'Ausgabe':
                                book['data']['edition'] = self.extract_content(td)

                        # set ISBN
                        if not 'isbn' in book['data']:
                            if field_name == u'ISBN/Einband/Preis':
                                isbn, more = self.extract_content(td).split(' ', 1)
                                book['data']['isbn'] = isbn

                        # set EAN
                        if not 'ean' in book['data']:
                            if field_name == u'EAN':
                                book['data']['ean'] = self.extract_content(td)

                        # find label
                        name_tag = td.find('strong')
                        if name_tag:
                            field_name = name_tag.string

            connection.close()
            # save the book
            self.save(book)
        return completion_successful