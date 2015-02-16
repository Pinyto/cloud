# coding=utf-8
"""
This File is part of Pinyto
"""


def extract_def_body(code):
    """
    takes an indented block of python code and removes the function declaration and the docblock.
    Indentations are reduced to the indentation in the main code block.

    :param code: The code of the function
    :type code: str
    :return: The function body with less indentation.
    :rtype: str
    """
    lines = code.splitlines()
    while lines[0].strip()[0] == '@':
        lines = lines[1:]
    indentation = lines[0].find('def')
    if indentation > 0:
        for line in lines:
            line = line[indentation:]
    return "\n".join(lines)