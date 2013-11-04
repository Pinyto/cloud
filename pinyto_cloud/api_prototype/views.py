from pymongo import MongoClient  # hmm
from service.database import remove_underscore_fields_list


class PinytoAPI(object):
    def __init__(self):
        self.db = MongoClient().pinyto.data  # hmm
        self.complete()

    def find(self, query):
        return remove_underscore_fields_list(self.db.find(query))

    def compress(self):
        pass

    def complete(self):
        pass

    def view(self, request):
        raise NotImplementedError("Please Implement this method")