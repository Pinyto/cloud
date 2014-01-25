# coding=utf-8
import unittest

from service.tests import database_tests, response_tests


def suite():
    """
    Test suite

    @return: [test suites]
    """
    tests_loader = unittest.TestLoader().loadTestsFromModule
    test_suites = [
        tests_loader(database_tests),
        tests_loader(response_tests)
    ]
    return unittest.TestSuite(test_suites)