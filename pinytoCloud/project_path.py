#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This file provides the convenience function project_path to specify paths
relative to the project path.
"""

from __future__ import division, print_function, unicode_literals
import os

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))


def project_path(filename):
    """
    project_path constructs an absolute path for project files and takes a filename
    or parts of a path as input.
    @param filename: string
    @return: sotring
    """
    return os.path.join(PROJECT_DIR, filename)

__all__ = ['project_path']