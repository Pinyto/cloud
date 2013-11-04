from pymongo import MongoClient  # hmm


class PinytoAPI(object):
    def __init__(self):
        self.db = MongoClient().pinyto  # hmm
        self.complete()

    def compress(self):
        pass

    def complete(self):
        pass

    def view(self):
        raise NotImplementedError("Please Implement this method")