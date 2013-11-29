# coding=utf-8
"""
This File is part of Pinyto
"""

from api_prototype.views import PinytoAPI
from service.response import *


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
            books = self.find({'type': 'book'})
            print(books)
            return json_response({'index': books})
        else:
            print("wrong Type")
            return False
