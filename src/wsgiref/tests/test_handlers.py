from __future__ import nested_scopes    # Backward compat for 2.1
from unittest import TestCase, TestSuite, makeSuite
from wsgiref.util import setup_testing_defaults
from wsgiref.headers import Headers
from wsgiref.handlers import BaseHandler, BaseCGIHandler
from StringIO import StringIO
import re

class ErrorHandler(BaseCGIHandler):
    """Simple handler subclass for testing BaseHandler"""

    def __init__(self,**kw):
        setup_testing_defaults(kw)
        BaseCGIHandler.__init__(
            self, StringIO(''), StringIO(), StringIO(), kw,
            multithread=True, multiprocess=True
        )

class TestHandler(ErrorHandler):
    """Simple handler subclass for testing BaseHandler, w/error passthru"""

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
            '_flush','get_stdin','get_stderr','add_cgi_vars'
        ]:
            self.assertRaises(NotImplementedError, getattr(h,name))
        self.assertRaises(NotImplementedError, h._write, "test")


    def testContentLength(self):
        # Demo one reason iteration is better than write()...  ;)

        def trivial_app1(e,s):
            s('200 OK',[])
            return [e['wsgi.url_scheme']]

        def trivial_app2(e,s):
            s('200 OK',[])(e['wsgi.url_scheme'])
            return []

        h = TestHandler()
        h.run(trivial_app1)
        self.assertEqual(h.stdout.getvalue(),
            "Status: 200 OK\r\n"
            "Content-Length: 4\r\n"
            "\r\n"
            "http")
        
        h = TestHandler()
        h.run(trivial_app2)
        self.assertEqual(h.stdout.getvalue(),
            "Status: 200 OK\r\n"
            "\r\n"
            "http")
        






    def testBasicErrorOutput(self):
        
        def non_error_app(e,s):
            s('200 OK',[])
            return []

        def error_app(e,s):
            raise AssertionError("This should be caught by handler")

        h = ErrorHandler()
        h.run(non_error_app)
        self.assertEqual(h.stdout.getvalue(),
            "Status: 200 OK\r\n"
            "Content-Length: 0\r\n"
            "\r\n")
        self.assertEqual(h.stderr.getvalue(),"")

        h = ErrorHandler()
        h.run(error_app)
        self.assertEqual(h.stdout.getvalue(),
            "Status: %s\r\n"
            "Content-Type: text/plain\r\n"
            "Content-Length: %d\r\n"
            "\r\n%s" % (h.error_status,len(h.error_body),h.error_body))

        self.failUnless(h.stderr.getvalue().find("AssertionError")<>-1)

    def testErrorAfterOutput(self):
        MSG = "Some output has been sent"
        def error_app(e,s):
            s("200 OK",[])(MSG)
            raise AssertionError("This should be caught by handler")

        h = ErrorHandler()
        h.run(error_app)
        self.assertEqual(h.stdout.getvalue(),
            "Status: 200 OK\r\n"
            "\r\n"+MSG)
        self.failUnless(h.stderr.getvalue().find("AssertionError")<>-1)


    def testHeaderFormats(self):

        def non_error_app(e,s):
            s('200 OK',[])
            return []

        stdpat = (
            r"HTTP/%s 200 OK\r\n"
            r"Date: \w{3} \w{3} [ 0123]\d \d\d:\d\d:\d\d \d{4}\r\n"
            r"%s" r"Content-Length: 0\r\n" r"\r\n"
        )
        shortpat = (
            "Status: 200 OK\r\n" "Content-Length: 0\r\n" "\r\n"
        )

        for ssw in "FooBar/1.0", None:
            sw = ssw and "Server: %s\r\n" % ssw or ""

            for version in "1.0", "1.1":           
                for proto in "HTTP/0.9", "HTTP/1.0", "HTTP/1.1":
                   
                    h = TestHandler(SERVER_PROTOCOL=proto)
                    h.origin_server = False
                    h.http_version = version
                    h.server_software = ssw
                    h.run(non_error_app)
                    self.assertEqual(shortpat,h.stdout.getvalue())
                
                    h = TestHandler(SERVER_PROTOCOL=proto)
                    h.origin_server = True
                    h.http_version = version
                    h.server_software = ssw
                    h.run(non_error_app)   
                    if proto=="HTTP/0.9":
                        self.assertEqual(h.stdout.getvalue(),"")
                    else:
                        self.failUnless(
                            re.match(stdpat%(version,sw), h.stdout.getvalue()),
                            (stdpat%(version,sw), h.stdout.getvalue())
                        )

TestClasses = (
    HandlerTests,
)

def test_suite():
    return TestSuite([makeSuite(t,'test') for t in TestClasses])



































