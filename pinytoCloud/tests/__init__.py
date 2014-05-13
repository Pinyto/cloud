# coding=utf-8
"""
This File is part of Pinyto
"""
import unittest

from pinytoCloud.tests import test_authentication


def suite():
    """
    Test suite

    @return: [test suites]
    """
    tests_loader = unittest.TestLoader().loadTestsFromModule
    test_suites = [
        tests_loader(test_authentication)
    ]
    return unittest.TestSuite(test_suites)