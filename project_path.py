#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This file provides the convenience function project_path to specify paths
relative to the project path.


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
