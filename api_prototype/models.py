# coding=utf-8
"""
This File is part of Pinyto
"""

from api_prototype.sandbox_helpers import piped_command
from api_prototype.sandbox_helpers import escape_all_objectids_and_datetime
from api_prototype.sandbox_helpers import unescape_all_objectids_and_datetime


class SandboxCollectionWrapper(object):
    """
    This wrapper is user to expose the db to the users assemblies.
    This is the class with the same methods to be used in the sandbox.
    """

    def __init__(self, child_pipe):
        self.child = child_pipe

    def find(self, query, skip=0, limit=0, sorting=None, sort_direction='asc'):
        """
        Use this function to read from the database. This method
        encodes all fields beginning with _ for returning a valid
        json response.

        :param query:
        :type query: dict
        :param skip: Count of documents which should be skipped in the query. This is useful for pagination.
        :type skip: int
        :param limit: Number of documents which should be returned. This number is of course the maximum.
        :type limit: int
        :param sorting: String identifying the key which is used for sorting.
        :type sorting: str
        :param sort_direction: 'asc' or 'desc'
        :type sort_direction: str
        :return: The list of found documents. If no document is found the list is empty.
        :rtype: list
        """
        return piped_command(self.child, {'db.find': {
            'query': query,
            'skip': skip,
            'limit': limit,
            'sorting': sorting,
            'sort_direction': sort_direction
        }})

    def count(self, query):
        """
        Use this function to get a count from the database.

        :param query:
        :type query: dict
        :return: The number of documents matching the query
        :rtype: int
        """
        return int(piped_command(self.child, {'db.count': {'query': query}}))

    def find_documents(self, query, skip=0, limit=0, sorting=None, sort_direction='asc'):
        """
        Use this function to read from the database. This method
        returns complete documents with _id fields. Do not use this
        to construct json responses!

        :param query:
        :type query: dict
        :param skip: Count of documents which should be skipped in the query. This is useful for pagination.
        :type skip: int
        :param limit: Number of documents which should be returned. This number is of course the maximum.
        :type limit: int
        :param sorting: String identifying the key which is used for sorting.
        :type sorting: str
        :param sort_direction: 'asc' or 'desc'
        :type sort_direction: str
        :return: The list of found documents. If no document is found the list is empty.
        :rtype: list
        """
        return [unescape_all_objectids_and_datetime(item) for item in piped_command(
            self.child,
            {
                'db.find_documents': {
                    'query': query,
                    'skip': skip,
                    'limit': limit,
                    'sorting': sorting,
                    'sort_direction': sort_direction
                }
            }
        )]

    def find_document_for_id(self, document_id):
        """
        Find the document with the given ID in the database. On
        success this returns a single document.

        :param document_id:
        :type document_id: string
        :return: The document with the given _id
        :rtype: dict
        """
        return unescape_all_objectids_and_datetime(
            piped_command(
                self.child,
                {'db.find_document_for_id': escape_all_objectids_and_datetime({'document_id': document_id})}
            )
        )

    def find_distinct(self, query, attribute):
        """
        Return a list representing the diversity of a given attribute in
        the documents matched by the query.

        :param query: json
        :type query: str
        :param attribute: String describing the attribute
        :type attribute: str
        :return: A list of values the attribute can have in the set of documents described by the query
        :rtype: list
        """
        return piped_command(self.child, {'db.find_distinct': {'query': query, 'attribute': attribute}})

    def save(self, document):
        """
        Saves the document. The document must have a valid _id

        :param document:
        :type document: dict
        :return: The ObjectId of the insrted document
        :rtype: str
        """
        document = escape_all_objectids_and_datetime(document)
        return piped_command(self.child, {'db.save': {'document': document}})

    def insert(self, document):
        """
        Inserts a document. If the given document has a ID the
        ID is removed and a new ID will be generated. Time will
        be set to now.

        :param document:
        :type document: dict
        :return: The ObjectId of the insrted document
        :rtype: str
        """
        document = escape_all_objectids_and_datetime(document)
        return piped_command(self.child, {'db.insert': {'document': document}})

    def remove(self, document):
        """
        Deletes the document. The document must have a valid _id

        :param document:
        :type document: dict
        """
        document = escape_all_objectids_and_datetime(document)
        return piped_command(self.child, {'db.remove': {'document': document}})


class SandboxRequestPost(object):
    """
    This wrapper is used to expose Django's request object to the users assemblies.
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

        :param param:
        :type param: str
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
        self.body = b""

    def init_body(self):
        """
        This needs to be called after the seccomp process is initialized to fill in valid body data for the request.
        """
        self.body = piped_command(self.child, {'request.body': {}}).encode('utf-8')


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

        :param class_name:
        :type class_name: str
        :param args: additional arguments
        :return: Objects of the type specified in class_name
        :rtype: Object
        """
        if class_name == 'ParseHtml':
            return SandboxParseHtml(self.pipe_child_end, *args)
        elif class_name == 'Http':
            return SandboxHttp(self.pipe_child_end)
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
        ``{'tag': 'tagname', 'attrs': dict}``

        :param descriptions:
        :type descriptions: dict
        :rtype: boolean
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
        ``{'tag': 'tag name', 'attrs': dict}``

        :param descriptions:
        :type descriptions: dict
        :param attribute:
        :type attribute: str
        :return: string or list if attribute is class
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
        ``{'tag': 'tag name', 'attrs': dict}``. The last description in this list will
        be used for a findAll of that element. This should select all the rows of the
        table you want to read.
        specify all the information you are searching for in searched_information in the
        following format: ``{'name': {'search tag': 'td', 'search attrs': dict,``
        ``'captions': ['list', 'of', 'captions'], 'content tag': 'td', 'content attrs': dict},``
        ``'next name': ...}``

        :param descriptions:
        :type descriptions: dict
        :param searched_information:
        :type searched_information: dict
        :rtype: dict
        """
        return piped_command(
            self.child,
            {'parsehtml.find_element_and_collect_table_like_information': {
                'target': self.target,
                'descriptions': descriptions,
                'searched_information': searched_information}})


class SandboxHttp():
    """
    This wrapper is user to expose http requests to the sandbox.
    This is the Http class with the same methods to be used in the sandbox.
    """

    def __init__(self, pipe_child_end):
        self.child = pipe_child_end

    def get(self, url):
        """
        This issues a http request to the supplied url and returns
        the response as a string. If the request fails an empty
        string is returned.

        :param url: Url with http:// or https:// at the beginning
        :type: str
        :rtype: str
        """
        return piped_command(
            self.child,
            {'https.get': {
                'url': url}})

    def post(self, url, data):
        """
        This issues a http request to the supplied url and returns
        the response as a string. If the request fails an empty
        string is returned.

        :param url: Url with http:// or https:// at the beginning
        :type url: str
        :param data: payload data
        :type data: dict
        :rtype: str
        """
        return piped_command(
            self.child,
            {'https.post': {
                'url': url,
                'data': data}})