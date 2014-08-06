# coding=utf-8
"""
This File is part of Pinyto
"""

from bs4 import NavigableString


def extract_content(tag):
        """
        Takes a tag and returns the string content without markup.

        @param tag: BeautifulSoup Tag
        @return: string
        """
        content = u''
        if not tag:
            return content
        for c in tag.contents:
            if not isinstance(c, NavigableString):
                content += extract_content(c)
            else:
                content += u' ' + unicode(c) + u' '
        return u' '.join(content.split())
