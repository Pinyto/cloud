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

from bs4 import BeautifulSoup
from service.xml import extract_content


class ParseHtml():
    """
    Use this service to get information from html documents.
    """
    def __init__(self, html):
        self.soup = BeautifulSoup(html, "html.parser")

    def contains(self, descriptions):
        """
        Use this function to check if the html contains the described tag.
        The descriptions must be a list of python dictionaries with
        ``{'tag': 'tagname', 'attrs': dict}``

        :param descriptions:
        :type descriptions: dict
        :rtype: boolean
        """
        if type(descriptions) == dict:
            descriptions = [descriptions]
        if type(descriptions) != list:
            return ""
        element = self.soup
        for description in descriptions:
            if 'tag' not in description or not (type(description['tag']) == str or type(description['tag']) == bytes):
                return False
            attrs_dict = {}
            if 'attrs' in description and type(description['attrs']) == dict:
                attrs_dict = description['attrs']
            element = element.find(description['tag'], attrs=attrs_dict)
            if not element:
                return False
        return True

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
        if type(descriptions) == dict:
            descriptions = [descriptions]
        if type(descriptions) != list:
            return ""
        element = self.soup
        for description in descriptions:
            if 'tag' not in description or \
               not (type(description['tag']) == str or type(description['tag']) == bytes):
                return ""
            attrs_dict = {}
            if 'attrs' in description and type(description['attrs']) == dict:
                attrs_dict = description['attrs']
            element = element.find(description['tag'], attrs=attrs_dict)
            if not element:
                return ""
        if attribute in element.attrs:
            return element[attribute]
        else:
            return ""

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
        if type(descriptions) == dict:
            descriptions = [descriptions]
        if type(descriptions) != list:
            return {}
        element = self.soup
        rows = []
        for i, description in enumerate(descriptions):
            if 'tag' not in description or \
               not (type(description['tag']) == str or type(description['tag']) == bytes):
                return {}
            attrs_dict = {}
            if 'attrs' in description and type(description['attrs']) == dict:
                attrs_dict = description['attrs']
            if i < len(descriptions) - 1:
                element = element.find(description['tag'], attrs=attrs_dict)
            else:
                rows = element.find_all(description['tag'], attrs=attrs_dict, recursive=False)
        results = {}
        for row in rows:
            for key in searched_information:
                tag = 'td'
                if 'search tag' in searched_information[key]:
                    tag = searched_information[key]['search tag']
                attrs_dict = {}
                if 'search attrs' in searched_information[key]:
                    attrs_dict = searched_information[key]['search attrs']
                captions = []
                if 'captions' in searched_information[key]:
                    captions = searched_information[key]['captions']
                caption_element = row.find(tag, attrs=attrs_dict)
                if extract_content(caption_element) in captions:
                    if 'content tag' in searched_information[key]:
                        tag = searched_information[key]['content tag']
                    attrs_dict = {}
                    if 'content attrs' in searched_information[key]:
                        attrs_dict = searched_information[key]['content attrs']
                    for element in row.find_all(tag, attrs=attrs_dict, recursive=False):
                        if element != caption_element:
                            results[key] = extract_content(element)
                            break
        return results