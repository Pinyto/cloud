# coding=utf-8
import unittest

from service.tests import test_database, test_response


def suite():
    """
    Test suite

    @return: [test suites]
    """
    tests_loader = unittest.TestLoader().loadTestsFromModule
    test_suites = [
        tests_loader(test_database),
        tests_loader(test_response)
    ]
    return unittest.TestSuite(test_suites)