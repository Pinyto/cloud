# coding=utf-8
"""
This File is part of Pinyto
"""

from bs4 import NavigableString


def extract_content(tag):
        """
        Takes a tag and returns the string content without markup.

        :param tag: BeautifulSoup Tag
        :rtype: str
        """
        content = ''
        if not tag:
            return content
        for c in tag.contents:
            if not isinstance(c, NavigableString):
                content += extract_content(c)
            else:
                content += ' ' + str(c) + ' '
        return ' '.join(content.split())
