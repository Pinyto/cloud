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

    def contains(self, description):
        """
        Use this function to check if the html contains the described tag.
        The description must be a python dictionary with
        {'tag': 'tagname', 'attrs': dict}
        @param description: dict
        @return: bool
        """
        if not 'tag' in description or not (type(description['tag']) == str or type(description['tag']) == unicode):
            return False
        attrs_dict = {}
        if 'attrs' in description and type(description['attrs']) == dict:
            attrs_dict = description['attrs']
        element = self.soup.find(description['tag'], attrs=attrs_dict)
        if element:
            return True
        else:
            return False

    def find_element_and_get_attribute_value(self, description, attribute):
        """
        Use this function to find the described tag and return the value from
        attribute if the tag is found. Returns empty string if the tag or the
        attribute is not found.
        The description must be a python dictionary with
        {'tag': 'tagname', 'attrs': dict}
        @param description: dict
        @param attribute: string
        @return: string or list if attribute is class
        """
        if not 'tag' in description or not (type(description['tag']) == str or type(description['tag']) == unicode):
            return False
        attrs_dict = {}
        if 'attrs' in description and type(description['attrs']) == dict:
            attrs_dict = description['attrs']
        element = self.soup.find(description['tag'], attrs=attrs_dict)
        if element:
            if attribute in element.attrs:
                return element[attribute]
        return ""