from unittest import TestSuite, TestCase, makeSuite

def compare_generic_iter(make_it,match):
    """Utility to compare a generic 2.1/2.2+ iterator with an iterable

    If running under Python 2.2+, this tests the iterator using iter()/next(),
    as well as __getitem__.  'make_it' must be a function returning a fresh
    iterator to be tested (since this may test the iterator twice)."""

    it = make_it()
    n = 0
    for item in match:
        assert it[n]==item
        n+=1
    try:
        it[n]
    except IndexError:
        pass
    else:
        raise AssertionError("Too many items from __getitem__",it)

    try:
        iter, StopIteration
    except NameError:
        pass
    else:
        # Only test iter mode under 2.2+
        it = make_it()
        assert iter(it) is it
        for item in match:
            assert it.next()==item
        try:
            it.next()
        except StopIteration:
            pass
        else:
            raise AssertionError("Too many items from .next()",it)




def test_suite():

    from wsgiref.tests import test_util
    from wsgiref.tests import test_headers

    tests = [
        test_util.test_suite(),
        test_headers.test_suite(),
    ]

    return TestSuite(tests)






























