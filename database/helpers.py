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

from __future__ import division, print_function, unicode_literals


def get_str_or_discard(data):
    """
    Get the string representation of data or return an empty
    string. Only numbers are converted.

    @param data: str or float or int
    @return: str
    """
    if type(data) in [str, float, int, bytes]:
        return str(data)
    else:
        return ""


def get_tags(tag_data):
    """
    Extracts the list of string tags from the data and discards
    everything else.

    @param tag_data: json
    @return: [string]
    """
    if type(tag_data) is str:
        return [tag_data]
    if type(tag_data) is list:
        tags = []
        for tag in tag_data:
            tag = get_str_or_discard(tag)
            if tag:
                tags.append(tag)
        return tags
    else:
        return []
