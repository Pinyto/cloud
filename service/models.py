# coding=utf-8
"""
Pinyto cloud - A secure cloud database for your personal data
Copyright (C) 2105 Johannes Merkert <jonny@pinyto.de>

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

from api_prototype.models import CanNotCreateNewInstanceInTheSandbox
from service.parsehtml import ParseHtml
from service.http import Http


class Factory():
    """
    Use this factory to create objects in outside the sandboxed
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

        :param class_name:
        :type class_name: str
        :param args: additional arguments
        :return: Objects of the type specified in class_name
        :rtype: Object
        """
        if class_name == 'ParseHtml':
            return ParseHtml(*args)
        elif class_name == 'Http':
            return Http()
        raise CanNotCreateNewInstanceInTheSandbox(class_name)