# coding=utf-8
"""
This File is part of Pinyto
"""
from __future__ import division, print_function, unicode_literals

from django.contrib.auth.models import User, Group


def create_user(username, mail="a@bc.de", password=None,
                groups=()):
    """
    Convenience function to add users.

    @param username: string
    @param mail: string
    @param password: string
    @param groups: tuple
    @return: User
    """
    if password:
        new_user = User.objects.create_user(username, mail, password)
    else:
        new_user = User(username=username, email=mail)
        new_user.save()
    for group in groups:
        Group.objects.get(name=group).user_set.add(new_user)

    return new_user


def get_str_or_discard(data):
    """
    Get the string representation of data or return an empty
    string. Only numbers are converted.

    @param data: str or float or int
    @return: str
    """
    if type(data) in [str, float, int]:
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