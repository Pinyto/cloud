# coding=utf-8
"""
This File is part of Pinyto
"""

from api_prototype.models import CanNotCreateNewInstanceInTheSandbox
from service.parsehtml import ParseHtml
from service.http import Https


class Factory():
    """
    Use this factory to create objects in the outside the sandboxed
    process. Just pass the class name to the create method.
    """

    def __init__(self):
        pass

    @staticmethod
    def create(class_name, *args):
        """
        This method will create an object of the class of classname
        with the arguments supplied after that. If the class can not
        be created in the sandbox it throws an Exception. The Exception
        gets thrown even if this is not executed inside the sandbox
        because every code should be executable in the sandbox.
        @param class_name: string
        @param args: additional arguments
        @return: Object
        """
        if class_name == 'ParseHtml':
            return ParseHtml(*args)
        elif class_name == 'Https':
            return Https()
        raise CanNotCreateNewInstanceInTheSandbox(class_name)