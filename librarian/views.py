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
        request_type = request.GET.get('type', 'index')
        if request_type == 'index':
            books = self.find({'type': 'book'})
            return json_response(books)
        else:
            return False
