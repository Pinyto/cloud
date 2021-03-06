# coding=utf-8
"""
Pinyto cloud - A secure cloud database for your personal data
Copyright (C) 2019 Pina Merkert <pina@pinae.net>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import json


class Librarian():
    """
    This is the Librarian.
    """
    def __init__(self):
        pass

    @staticmethod
    def index(request, db, factory):
        """
        index returns the specified book if a ean or isbn is given and all books if not.
        It never returns more than 42 books.

        @param request: Django Request
        @param db: DatabaseWrapper
        @param factory: Factory (either service.models.Factory or api_prototype.models.Factory)
        @return: string
        """
        try:
            data = json.loads(str(request.body, encoding='utf-8'))
        except ValueError:
            return {'error': 'The data you supplied is not valid json.'}
        if 'ean' in data:
            books = db.find({'type': 'book', 'data.ean': data['ean']}, skip=0, limit=42)
        elif 'isbn' in data:
            books = db.find({'type': 'book', 'data.isbn': data['isbn']}, skip=0, limit=42)
        else:
            books = db.find({'type': 'book'}, skip=0, limit=42)
        return {'index': books}

    @staticmethod
    def search(request, db, factory):
        """
        search returns all books which have the searchstring in the title, the uniform_title,
        the publisher name, the year, the category or the author. It never returns more than
        42 books.

        @param request: Django Request
        @param db: DatabaseWrapper
        @param factory: Factory (either service.models.Factory or api_prototype.models.Factory)
        @return: string
        """
        try:
            search_string = json.loads(str(request.body, encoding='utf-8'))['searchstring']
        except ValueError:
            return {'error': 'The data you supplied is not valid json.'}
        except IndexError:
            search_string = ""
        books = db.find({'type': 'book',
                         'data': {'$exists': True},
                         '$or': [
                             {'data.title': {'$regex': search_string, '$options': 'i'}},
                             {'data.uniform_title': {'$regex': search_string, '$options': 'i'}},
                             {'data.publisher': {'$regex': search_string, '$options': 'i'}},
                             {'data.year': {'$regex': search_string, '$options': 'i'}},
                             {'data.category': {'$regex': search_string, '$options': 'i'}},
                             {'data.author': {'$regex': search_string, '$options': 'i'}}
                         ]}, skip=0, limit=42)
        return {'index': books}

    @staticmethod
    def update(request, db, factory):
        """
        update gets data with an _id and searches the document with this _id. If found
        it updates the document and saves the changes.

        @param request: Django Request
        @param db: DatabaseWrapper
        @param factory: Factory (either service.models.Factory or api_prototype.models.Factory)
        @return: string
        """
        try:
            book_data = json.loads(str(request.body, encoding='utf-8'))['book']
        except IndexError:
            return {'error': 'You have to supply a book to update.'}
        except ValueError:
            return {'error': 'The data you supplied is not valid json.'}
        if 'type' not in book_data:
            return {'error': 'The data you supplied has no type. Please supply a book with type: book.'}
        if book_data['type'] != 'book':
            return {'error': 'This is not a book.'}
        if '_id' not in book_data:
            return {'error': 'You have to specify an _id to identify the book you want to update.'}
        book = db.find_document_for_id(book_data['_id'])
        if not book:  # there was an error
            return {'error': 'There is no book with this ID which could be updated.'}
        for key in book_data['data']:
            book['data'][key] = book_data['data'][key]
        db.save(book)
        return {'success': True}

    @staticmethod
    def update_all(request, db, factory):
        """
        update_all updates all books which have the given isbn or ean.

        @param request: Django Request
        @param db: DatabaseWrapper
        @param factory: Factory (either service.models.Factory or api_prototype.models.Factory)
        @return: string
        """
        try:
            book_data = json.loads(str(request.body, encoding='utf-8'))['book']
        except IndexError:
            return {'error': 'You have to supply a book to update.'}
        except ValueError:
            return {'error': 'The data you supplied is not valid json.'}
        if 'type' not in book_data:
            return {'error': 'The data you supplied has no type. Please supply a book with type: book.'}
        if book_data['type'] != 'book':
            return {'error': 'This is not a book.'}
        if 'isbn' in book_data['data']:
            books = list(db.find_documents({'type': 'book',
                                            'data': {'$exists': True},
                                            'data.isbn': book_data['data']['isbn']}))
        elif 'ean' in book_data['data']:
            books = list(db.find_documents({'type': 'book',
                                            'data': {'$exists': True},
                                            'data.ean': book_data['data']['ean']}))
        else:
            books = []
        if not books:  # there was an error
            return {'error': 'There are no books with this ISBN or EAN which could be updated.'}
        for key in book_data['data']:
            for book in books:
                book['data'][key] = book_data['data'][key]
        for book in books:
            db.save(book)
        return {'success': True}

    @staticmethod
    def duplicate(request, db, factory):
        """
        duplicate duplicates the book specified by the _id.

        @param request: Django Request
        @param db: DatabaseWrapper
        @param factory: Factory (either service.models.Factory or api_prototype.models.Factory)
        @return: string
        """
        try:
            book_data = json.loads(str(request.body, encoding='utf-8'))['book']
        except IndexError:
            return {'error': 'You have to supply a book to duplicate.'}
        except ValueError:
            return {'error': 'The data you supplied is not valid json.'}
        if book_data['type'] != 'book':
            return {'error': 'This is not a book.'}
        if '_id' not in book_data:
            return {'error': 'You have to specify an _id to identify the book you want to duplicate.'}
        book = db.find_document_for_id(book_data['_id'])
        if not book:  # there was an error
            return {'error': 'There is no book with this ID which could be updated.'}
        for key in book_data['data']:
            book['data'][key] = book_data['data'][key]
        db.insert(book)
        return {'success': True}

    @staticmethod
    def remove(request, db, factory):
        """
        remove removes the book specified by the _id.

        @param request: Django Request
        @param db: DatabaseWrapper
        @param factory: Factory (either service.models.Factory or api_prototype.models.Factory)
        @return: string
        """
        try:
            book_data = json.loads(str(request.body, encoding='utf-8'))['book']
        except IndexError:
            return {'error': 'You have to supply a book to remove.'}
        except ValueError:
            return {'error': 'The data you supplied is not valid json.'}
        if book_data['type'] != 'book':
            return {'error': 'This is not a book.'}
        if '_id' not in book_data:
            return {'error': 'You have to specify an _id to identify the book you want to remove.'}
        book = db.find_document_for_id(book_data['_id'])
        if not book:  # there was an error
            return {'error': 'There is no book with this ID which could be deleted.'}
        db.remove(book)
        return {'success': True}

    @staticmethod
    def statistics(request, db, factory):
        """
        statistics returns the total count of books, the places where they are and how many are lent
        to somebody.

        @param request: Django Request
        @param db: DatabaseWrapper
        @param factory: Factory (either service.models.Factory or api_prototype.models.Factory)
        @return: string
        """
        return {
            'book_count': db.count({'type': 'book'}),
            'places_used': db.find_distinct(
                {'type': 'book', 'data': {'$exists': True}}, 'data.place'),
            'lent_count': db.count({'type': 'book',
                                    'data': {'$exists': True},
                                    'data.lent': {'$exists': True, '$ne': ""}})
        }

    @staticmethod
    def job_complete_data_by_asking_dnb(db, factory):
        """
        This job searches for books with incomplete data and asks the website of th german
        national library portal.dnb.de for the record of this book. The response gets parsed
        and the books are saved with the completed data.
        This is especially useful for the librarian as you are able to scan just the EAN of a
        book and let this job do the rest for you.

        @param db: DatabaseWrapper
        @param factory: Factory (either service.models.Factory or api_prototype.models.Factory)
        @return: nothing
        """
        incomplete_books = db.find_documents({'type': 'book',
                                              'data': {'$exists': True},
                                              '$or': [
                                                  {'data.author': {'$exists': False}},
                                                  {'data.title': {'$exists': False}},
                                                  {'data.uniform_title': {'$exists': False}},
                                                  {'data.isbn': {'$exists': False}},
                                                  {'data.ean': {'$exists': False}}
                                              ]})
        http = factory.create('Http')
        for book in incomplete_books:
            query = ''
            if 'isbn' in book['data']:
                query = book['data']['isbn']
            if 'ean' in book['data']:
                query = book['data']['ean']
            content = http.get('https://portal.dnb.de/opac.htm?query=' + query + '&method=simpleSearch')
            if not content:
                continue
            soup = factory.create('ParseHtml', content)
            if not soup.contains([
                {'tag': 'table',
                 'attrs': {'summary': "Vollanzeige des Suchergebnises"}}  # They have a typo here!
            ]):
                # we probably found a list of results. lets check for that
                link = soup.find_element_and_get_attribute_value(
                    [{'tag': 'table', 'attrs': {'summary': "Suchergebnis"}},  # They have a typo here too!
                     {'tag': 'a'}],
                    'href')
                if link:
                    content = http.get('https://portal.dnb.de' + link)
                    soup = factory.create('ParseHtml', content)
            parsed = soup.find_element_and_collect_table_like_information(
                [
                    {'tag': 'table',
                     'attrs': {
                         'summary': "Vollanzeige des Suchergebnises"}},
                    # They have a typo here!
                    {'tag': 'tr'}
                ], {
                    'author': {'search tag': 'td', 'captions': ['Person(en)'], 'content tag': 'td'},
                    'title': {'search tag': 'td',
                              'captions': [
                                  'Mehrteiliges Werk',
                                  'Titel',
                                  'Titel/Bezeichnung'],
                              'content tag': 'td'},
                    'uniform title': {'search tag': 'td', 'captions': ['Einheitssachtitel'], 'content tag': 'td'},
                    'year': {'search tag': 'td', 'captions': ['Erscheinungsjahr'], 'content tag': 'td'},
                    'languages': {'search tag': 'td', 'captions': ['Sprache(n)'], 'content tag': 'td'},
                    'category': {'search tag': 'td', 'captions': ['Sachgruppe(n)'], 'content tag': 'td'},
                    'publisher': {'search tag': 'td', 'captions': ['Verleger'], 'content tag': 'td'},
                    'edition': {'search tag': 'td', 'captions': ['Ausgabe'], 'content tag': 'td'},
                    'isbn': {'search tag': 'td', 'captions': ['ISBN/Einband/Preis'], 'content tag': 'td'},
                    'ean': {'search tag': 'td', 'captions': ['EAN'], 'content tag': 'td'}
                }
            )
            for key in parsed:
                if key not in book['data']:
                    book['data'][key] = parsed[key]
            db.save(book)
