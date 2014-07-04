# coding=utf-8
"""
This File is part of Pinyto
"""
import unittest

from service.tests import test_database, test_response, test_parsehtml, test_http


def suite():
    """
    Test suite

    @return: [test suites]
    """
    tests_loader = unittest.TestLoader().loadTestsFromModule
    test_suites = [
        tests_loader(test_database),
        tests_loader(test_response),
        tests_loader(test_parsehtml),
        tests_loader(test_http)
    ]
    return unittest.TestSuite(test_suites)