from __future__ import nested_scopes    # Backward compat for 2.1
from unittest import TestCase, TestSuite, makeSuite
from wsgiref.util import setup_testing_defaults
from wsgiref.handlers import BaseHandler, BaseCGIHandler
from StringIO import StringIO


class TestHandler(BaseCGIHandler):
    """Simple handler subclass for testing BaseHandler"""

    def __init__(self,**kw):
        setup_testing_defaults(kw)
        BaseCGIHandler.__init__(
            self, StringIO(''), StringIO(), StringIO(), kw,
            multithread=True, multiprocess=True
        )

    def handle_error(self):
        raise   # for testing, we want to see what's happening






















class HandlerTests(TestCase):

    def checkEnvironAttrs(self, handler):
        env = handler.environ
        for attr in [
            'version','multithread','multiprocess','run_once','file_wrapper'
        ]:
            if attr=='file_wrapper' and handler.wsgi_file_wrapper is None:
                continue
            self.assertEqual(getattr(handler,'wsgi_'+attr),env['wsgi.'+attr])

    def checkOSEnviron(self,handler):
        empty = {}; setup_testing_defaults(empty)
        env = handler.environ
        from os import environ
        for k,v in environ.items():
            if not empty.has_key(k):
                self.assertEqual(env[k],v)
        for k,v in empty.items():
            self.failUnless(env.has_key(k))

    def testEnviron(self):
        h = TestHandler(X="Y")
        h.setup_environ()
        self.checkEnvironAttrs(h)
        self.checkOSEnviron(h)
        self.assertEqual(h.environ["X"],"Y")

    def testCGIEnviron(self):
        h = BaseCGIHandler(None,None,None,{})
        h.setup_environ()
        for key in 'wsgi.url_scheme', 'wsgi.input', 'wsgi.errors':
            assert h.environ.has_key(key)

    def testScheme(self):
        h=TestHandler(HTTPS="on"); h.setup_environ()
        self.assertEqual(h.environ['wsgi.url_scheme'],'https')
        h=TestHandler(); h.setup_environ()
        self.assertEqual(h.environ['wsgi.url_scheme'],'http')


    def testAbstractMethods(self):
        h = BaseHandler()
        for name in [
            'handle_error','_flush','get_stdin','get_stderr','add_cgi_vars'
        ]:
            self.assertRaises(NotImplementedError, getattr(h,name))
        self.assertRaises(NotImplementedError, h._write, "test")


    def testSimpleRun(self):
        h = TestHandler()
        h.run(lambda e,s: [(s('200 OK',[]) or 1) and e['wsgi.url_scheme']])
        self.assertEqual(h.stdout.getvalue(),"Status: 200 OK\r\n\r\nhttp")
        





TestClasses = (
    HandlerTests,
)

def test_suite():
    return TestSuite([makeSuite(t,'test') for t in TestClasses])



































