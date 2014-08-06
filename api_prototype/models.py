# coding=utf-8
"""
This File is part of Pinyto
"""

from api_prototype.sandbox_helpers import piped_command, escape_all_objectids, unescape_all_objectids
from base64 import b64decode


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
        return [unescape_all_objectids(item) for item in piped_command(
            self.child,
            {'db.find_documents': {'query': query, 'limit': limit}}
        )]

    def find_document_for_id(self, document_id):
        """
        Find the document with the given ID in the database. On
        success this returns a single document.

        @param document_id: string
        @return: dict
        """
        return unescape_all_objectids(
            piped_command(
                self.child,
                {'db.find_document_for_id': escape_all_objectids({'document_id': document_id})}
            )
        )

    def find_distinct(self, query, attribute):
        """
        Return a list representing the diversity of a given attribute in
        the documents matched by the query.

        @param query: json string
        @param attribute:
        @return:
        """
        return piped_command(self.child, {'db.find_distinct': {'query': query, 'attribute': attribute}})

    def save(self, document):
        """
        Saves the document. The document must have a valid _id

        @param document:
        @return:
        """
        document = escape_all_objectids(document)
        return piped_command(self.child, {'db.save': {'document': document}})

    def insert(self, document):
        """
        Inserts a document. If the given document has a ID the
        ID is removed and a new ID will be generated. Time will
        be set to now.

        @param document:
        @return:
        """
        document = escape_all_objectids(document)
        return piped_command(self.child, {'db.insert': {'document': document}})

    def remove(self, document):
        """
        Deletes the document. The document must have a valid _id

        @param document:
        @return:
        """
        document = escape_all_objectids(document)
        return piped_command(self.child, {'db.remove': {'document': document}})


class SandboxRequestPost(object):
    """
    This wrapper is user to expose Django's request object to the users assemblies.
    This class implements the most used methods of the request object.

    This class is used to emulate request.POST
    """

    def __init__(self, child_pipe):
        self.child = child_pipe

    def __getitem__(self, item):
        """
        This enables array-like access
        """
        return piped_command(self.child, {'request.post.get': {'param': item}})

    def get(self, param):
        """
        Returns the specified param
        """
        return piped_command(self.child, {'request.post.get': {'param': param}})


class SandboxRequest(object):
    """
    This wrapper is user to expose Django's request object to the users assemblies.
    This class implements the most used methods of the request object.
    """

    def __init__(self, child_pipe):
        self.child = child_pipe
        self.POST = SandboxRequestPost(child_pipe)


class CanNotCreateNewInstanceInTheSandbox(Exception):
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

    def create(self, class_name, *args):
        """
        This method will create an object of the class of classname
        with the arguments supplied after that. If the class can not
        be created in the sandbox it throws an Exception.
        @param class_name: string
        @param args: additional arguments
        @return: Object
        """
        if class_name == 'ParseHtml':
            return SandboxParseHtml(self.pipe_child_end, *args)
        elif class_name == 'Https':
            return SandboxHttps(self.pipe_child_end)
        raise CanNotCreateNewInstanceInTheSandbox(class_name)


class SandboxParseHtml():
    """
    This wrapper is user to expose html parsing functionality to the sandbox.
    This is the ParseHtml class with the same methods to be used in the sandbox.
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


class SandboxHttps():
    """
    This wrapper is user to expose https requests to the sandbox.
    This is the Https class with the same methods to be used in the sandbox.
    """

    def __init__(self, pipe_child_end):
        self.child = pipe_child_end

    def get(self, domain, path):
        """
        This issues a http request to the supplied url and returns
        the response as a string. If the request fails an empty
        string is returned.

        @param domain: string
        @param path: string
        @return: string
        """
        return b64decode(piped_command(
            self.child,
            {'https.get': {
                'domain': domain,
                'path': path}}))

    def post(self, domain, path):
        """
        This issues a http request to the supplied url and returns
        the response as a string. If the request fails an empty
        string is returned.

        @param domain: string
        @param path: string
        @return: string
        """
        return b64decode(piped_command(
            self.child,
            {'https.post': {
                'domain': domain,
                'path': path}}))