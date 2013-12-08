# coding=utf-8
"""
This File is part of Pinyto
"""
from datetime import datetime


def remove_underscore_fields(data):
    """
    Removes _id

    @param data: dict
    @return: dict
    """
    converted = {}
    for key in data:
        if key[0] != '_':
            if key == 'time':
                converted[key] = (data[key] - datetime(1970, 1, 1)).total_seconds()
            else:
                converted[key] = data[key]
    return converted


def remove_underscore_fields_list(data_list):
    """
    Removes _id for every dict in the list

    @param data_list: [dict]
    @return: [dict]
    """
    converted_list = []
    for item in data_list:
        converted_list.append(remove_underscore_fields(item))
    return converted_list