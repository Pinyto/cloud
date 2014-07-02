# coding=utf-8
"""
This File is part of Pinyto
"""

from bs4 import BeautifulSoup


class ParseHtml():
    """
    Use this service to get information from html documents.
    """
    def __init__(self, html):
        self.soup = BeautifulSoup(html)

    def contains(self, descriptions):
        """
        Use this function to check if the html contains the described tag.
        The descriptions must be a list of python dictionaries with
        {'tag': 'tagname', 'attrs': dict}
        @param descriptions: [dict]
        @return: bool
        """
        if type(descriptions) == dict:
            descriptions = [descriptions]
        if type(descriptions) != list:
            return ""
        element = self.soup
        for description in descriptions:
            if not 'tag' in description or not (type(description['tag']) == str or type(description['tag']) == unicode):
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
        {'tag': 'tag name', 'attrs': dict}
        @param descriptions: [dict]
        @param attribute: string
        @return: string or list if attribute is class
        """
        if type(descriptions) == dict:
            descriptions = [descriptions]
        if type(descriptions) != list:
            return ""
        element = self.soup
        for description in descriptions:
            if not 'tag' in description or \
               not (type(description['tag']) == str or type(description['tag']) == unicode):
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