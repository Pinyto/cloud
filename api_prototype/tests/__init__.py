# coding=utf-8
"""
This File is part of Pinyto
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