from unittest import TestSuite, TestCase, makeSuite

def test_suite():

    from wsgiref.tests import test_util

    tests = [
        test_util.test_suite(),
    ]

    return TestSuite(tests)







