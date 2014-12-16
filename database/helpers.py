# coding=utf-8
"""
This File is part of Pinyto
"""
from __future__ import division, print_function, unicode_literals


def get_str_or_discard(data):
    """
    Get the string representation of data or return an empty
    string. Only numbers are converted.

    @param data: str or float or int
    @return: str
    """
    if type(data) in [str, float, int, unicode]:
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