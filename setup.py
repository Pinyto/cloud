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

import os
from setuptools import setup


def read(fname):
    """
    Utility function to read the README file.

    :param fname: Filename to be read
    :type fname: str
    :return: Contents of the specified file.
    :rtype: str
    """
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="pinyo-cloud",
    version="1.0.0",
    author="Johannes Merkert",
    author_email="jonny@pinyto.de",
    description="Pinyto cloud - A secure cloud database for your personal data",
    license="GPLv3",
    keywords="pinyto cloud database privacy remote-execution django angular",
    url="https://www.pinyto.de",
    packages=['api', 'api_prototype', 'database', 'keyserver', 'pinytoCloud', 'service'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Cloud",
        "License :: OSI Approved :: GPLv3 License",
    ],
)