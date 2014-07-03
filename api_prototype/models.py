# coding=utf-8
"""
This File is part of Pinyto
"""

from api_prototype.sandbox_helpers import write_to_pipe, read_from_pipe, piped_command


class SandboxCollectionWrapper(object):
    """
    This wrapper is user to expose the db to the users assemblies.
    This is the class with the same methods to be used in the sandbox.
    """

    def __init__(self, child_pipe):
        self.child = child_pipe

    def find(self, query, limit=0):
        """
        Use this function to read from the database. This method
        encodes all fields beginning with _ for returning a valid
        json response.

        @param query: json string
        @param limit: int
        @return: dict
        """
        return piped_command(self.child, {'db.find': {'query': query, 'limit': limit}})

    def count(self, query):
        """
        Use this function to get a count from the database.

        @param query: json string
        @return: dict
        """
        return int(piped_command(self.child, {'db.count': {'query': query}}))

    def find_documents(self, query, limit=0):
        """
        Use this function to read from the database. This method
        returns complete documents with _id fields. Do not use this
        to construct json responses!

        @param query: json string
        @param limit: integer
        @return: dict
        """
        return piped_command(self.child, {'db.find_documents': {'query': query, 'limit': limit}})

    def find_document_for_id(self, document_id):
        """
        Find the document with the given ID in the database. On
        success this returns a single document.

        @param document_id: string
        @return: dict
        """
        return piped_command(self.child, {'db.find_document_for_id': {'document_id': document_id}})

    def save(self, document):
        """
        Saves the document. The document must have a valid _id

        @param document:
        @return:
        """
        return piped_command(self.child, {'db.save': {'document': document}})

    def insert(self, document):
        """
        Inserts a document. If the given document has a ID the
        ID is removed and a new ID will be generated. Time will
        be set to now.

        @param document:
        @return:
        """
        return piped_command(self.child, {'db.insert': {'document': document}})

    def remove(self, document):
        """
        Deletes the document. The document must have a valid _id

        @param document:
        @return:
        """
        return piped_command(self.child, {'db.remove': {'document': document}})


class CanNotBeInstanciatedInTheSandbox(Exception):
    """
    This Exception is thrown if a script wants to create an object of a class
    that can not be created in the sandbox.
    """
    def __init__(self, class_name):
        self.class_name = class_name

    def __str__(self):
        return "Objects of type " + self.class_name + "can not be instanciated in the sandbox."


class Factory():
    """
    Use this factory to create objects in the sandboxed process. Just
    pass the class name to the create method.
    """

    def __init__(self, pipe_child_end):
        self.pipe_child_end = pipe_child_end

    def create(self, classname, *args):
        """
        This method will create an object of the class of classname
        with the arguments supplied after that. If the class can not
        be created in the sandbox it throws an Exception.
        """
        if classname == 'ParseHtml':
            return SandboxParseHtml(self.pipe_child_end, *args)
        raise CanNotBeInstanciatedInTheSandbox(classname)


class SandboxParseHtml():
    """
    This wrapper is user to expose html parsing functionality to the sandbox.
    This is the class with the same methods to be used in the sandbox.
    """

    def __init__(self, pipe_child_end, html):
        self.child = pipe_child_end
        self.target = piped_command(self.child, {'parsehtml.init': {'html': html}})

    def contains(self, descriptions):
        """
        Use this function to check if the html contains the described tag.
        The descriptions must be a list of python dictionaries with
        {'tag': 'tagname', 'attrs': dict}
        @param descriptions: [dict]
        @return: bool
        """
        return piped_command(
            self.child,
            {'parsehtml.contains': {
                'target': self.target,
                'descriptions': descriptions}})

    def find_element_and_get_attribute_value(self, descriptions, attribute):
        """
        Use this function to find the described tag and return the value from
        attribute if the tag is found. Returns empty string if the tag or the
        attribute is not found.
        The descriptions must be a list of python dictionaries with
        {'tag': 'tag name', 'attrs': dict}
        @param descriptions: [dict]
        @param attribute: string
        @return: string or list if attribute is class
        """
        return piped_command(
            self.child,
            {'parsehtml.find_element_and_get_attribute_value': {
                'target': self.target,
                'descriptions': descriptions,
                'attribute': attribute}})

    def find_element_and_collect_table_like_information(self, descriptions, searched_information):
        """
        If you are retrieving data from websites you might need to get the contents
        of a table or a similar structure. This is the function to get that information.
        The descriptions must be a list of python dictionaries with
        {'tag': 'tag name', 'attrs': dict}. The last description in this list will
        be used for a findAll of that element. This should select all the rows of the
        table you want to read.
        specify all the information you are searching for in searched_information in the
        following format: {'name': {'search tag': 'td', 'search attrs': dict,
        'captions': ['list', 'of', 'captions'], 'content tag': 'td', 'content attrs': dict},
        'next name': ...}
        @param descriptions: [dict]
        @param searched_information: dict
        @return: dict
        """
        return piped_command(
            self.child,
            {'parsehtml.find_element_and_collect_table_like_information': {
                'target': self.target,
                'descriptions': descriptions,
                'searched_information': searched_information}})
