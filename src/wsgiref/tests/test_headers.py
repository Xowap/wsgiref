from unittest import TestCase, TestSuite, makeSuite
from wsgiref.headers import Headers
from wsgiref.tests import compare_generic_iter


class HeaderTests(TestCase):

    def testMappingInterface(self):
        test = [('x','y')]
        self.assertEqual(len(Headers([])),0)
        self.assertEqual(len(Headers(test[:])),1)
        self.assertEqual(Headers(test[:]).keys(), ['x'])
        self.assertEqual(Headers(test[:]).values(), ['y'])
        self.assertEqual(Headers(test[:]).items(), test)
        self.failIf(Headers(test).items() is test)  # must be copy!

        h=Headers([])
        del h['foo']   # should not raise an error

        h['Foo'] = 'bar'
        for m in h.has_key, h.__contains__, h.get, h.get_all, h.__getitem__:
            self.failUnless(m('foo'))
            self.failUnless(m('Foo'))
            self.failUnless(m('FOO'))
            self.failIf(m('bar'))

        self.assertEqual(h['foo'],'bar')
        h['foo'] = 'baz'
        self.assertEqual(h['FOO'],'baz')
        self.assertEqual(h.get_all('foo'),['baz'])

        self.assertEqual(h.get("foo","whee"), "baz")
        self.assertEqual(h.get("zoo","whee"), "whee")

    def testRequireList(self):
        self.assertRaises(TypeError, Headers, "foo")





    def testExtras(self):
        h = Headers([])
        self.assertEqual(str(h),'\r\n')

        h.add_header('foo','bar',baz="spam")
        self.assertEqual(h['foo'], 'bar; baz="spam"')
        self.assertEqual(str(h),'foo: bar; baz="spam"\r\n\r\n')

        h.add_header('Foo','bar',cheese=None)
        self.assertEqual(h.get_all('foo'),
            ['bar; baz="spam"', 'bar; cheese'])

        self.assertEqual(str(h),
            'foo: bar; baz="spam"\r\n'
            'Foo: bar; cheese\r\n'
            '\r\n'
        )
























TestClasses = (
    HeaderTests,
)

def test_suite():
    return TestSuite([makeSuite(t,'test') for t in TestClasses])



































