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
