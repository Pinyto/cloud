from api_prototype.views import PinytoAPI
from service.response import *


class Librarian(PinytoAPI):
    def view(self, request):
        request_type = request.GET.get('type', 'index')
        if request_type == 'index':
            books = self.find({'type': 'book'})
            return json_response(books)
        else:
            return json_response(
                {'error': "The type of your request didn't match a known type. Please use one of [index] or no type."})
