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

import unittest

from api_prototype.tests import test_sandbox, test_sandbox_helpers


def suite():
    """
    Test suite

    @return: [test suites]
    """
    tests_loader = unittest.TestLoader().loadTestsFromModule
    test_suites = [
        tests_loader(test_sandbox),
        tests_loader(test_sandbox_helpers)
    ]
    return unittest.TestSuite(test_suites)