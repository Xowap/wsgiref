from types import StringType
from util import FileWrapper, guess_scheme
from headers import Headers

import sys, os

try:
    dict
except NameError:
    def dict(items):
        d = {}
        for k,v in items:
            d[k] = v
        return d

try:
    True
    False
except NameError:
    True = not None
    False = not True




















class BaseHandler:
    """Manage the invocation of a WSGI application"""

    wsgi_version = (1,0)
    wsgi_multithread = True
    wsgi_multiprocess = True
    wsgi_last_call = False

    # os_environ may be overridden at class or instance level, if desired
    os_environ = dict(os.environ.items())   

    # Collaborator classes
    wsgi_file_wrapper = FileWrapper     # set to None to disable
    headers_class = Headers             # must be a Headers-like class

    # State variables
    status = result = None
    headers_sent = False
    headers = None
    bytes_sent = 0


    def run(self, application):
        """Invoke the application"""
        try:
            self.setup_environ()
            self.result = application(self.environ, self.start_response)
            self.finish_response()
        except:
            self.handle_error()
            self.close()










    def setup_environ(self):
        """Set up the environment for one request"""

        env = self.environ = self.os_environ.copy()
        self.add_cgi_vars()

        env['wsgi.input']        = self.get_stdin()
        env['wsgi.errors']       = self.get_stderr()
        env['wsgi.version']      = self.wsgi_version
        env['wsgi.last_call']    = self.wsgi_last_call
        env['wsgi.url_scheme']   = self.get_scheme()
        env['wsgi.multithread']  = self.wsgi_multithread
        env['wsgi.multiprocess'] = self.wsgi_multiprocess

        if self.wsgi_file_wrapper is not None:
            env['wsgi.file_wrapper'] = self.wsgi_file_wrapper


    def finish_response(self):
        """Send any iterable data, then close self and the iterable

        Subclasses intended for use in asynchronous servers will
        probably want to redefine this method, such that it sets up
        callbacks to iterate over the data, and to call 'self.close()'
        when finished.
        """
        try:
            try:
                if not self.result_is_file() and not self.sendfile():
                    for data in self.result:
                        self.write(data)
                    self.finish_content()
            except:
                self.handle_error()
        finally:
            self.close()





    def get_scheme(self):
        """Return the URL scheme being used"""
        return guess_scheme(self.environ)


    def cleanup_headers(self):
        """Make any necessary header changes or defaults"""
        # XXX set up Content-Length, chunked encoding, if possible/needed


    def start_response(self, status, headers,exc_info=None):
        """'start_response()' callable as specified by PEP 333"""

        if exc_info:
            try:
                if self.headers_sent:
                    # Re-raise original exception if headers sent
                    raise exc_info[0], exc_info[1], exc_info[2]
            finally:
                exc_info = None        # avoid dangling circular ref
        elif self.headers is not None:
            raise AssertionError("Headers already set!")

        assert type(status) is StringType,"Status must be a string"
        assert len(status)>=4,"Status must be at least 4 characters"
        assert int(status[:3]),"Status message must begin w/3-digit code"
        assert status[3]==" ", "Status message must have a space after code"
        if __debug__:
            for name,val in headers:
                assert type(name) is StringType,"Header names must be strings"
                assert type(val) is StringType,"Header values must be strings"

        self.status = status
        self.headers = self.headers_class(headers)
        return self.write






    def write(self, data):
        """'write()' callable as specified by PEP 333"""

        assert type(data) is StringType,"write() argument must be string"

        if not self.status:
             raise AssertionError("write() before start_response()")

        elif not self.headers_sent:
             # Before the first output, send the stored headers
             self.send_headers()

        self.bytes_sent += len(data)
        # XXX check Content-Length and truncate if too many bytes written?
        self._write(data)
        self._flush()


    def sendfile(self):
        """Platform-specific file transmission

        Override this method in subclasses to support platform-specific
        file transmission.  It is only called if the application's
        return iterable ('self.result') is an instance of
        'self.wsgi_file_wrapper'.

        This method should return a true value if it is able to
        transmit the wrapped file-like object using a platform-specific
        approach.  It should return a false value if normal iteration
        should be used instead.  An exception can be raised to indicate
        that transmission was attempted, but failed.

        NOTE: this method should call 'self.send_headers()' if it is
        going to attempt direct transmission, and 'self.headers_sent'
        is false.
        """
        return False   # No platform-specific transmission by default




    def finish_content(self):
        """Ensure headers and content have both been sent"""
        if not self.headers_sent:
            self.headers['Content-Length'] = "0"
            self.send_headers()
        else:
            pass # XXX check if content-length was too short?

    def close(self):
        """Close the iterable, if needed, and reset all instance vars

        Subclasses may want to also drop the client connection.
        """
        if hasattr(self.result,'close'):
            self.result.close()
        self.result = self.headers = self.status = self.environ = None
        self.bytes_sent = 0
        self.headers_sent = False


    def send_status(self):
        """Transmit the status to the client, via self._write()

        (BaseCGIHandler overrides this to use a "Status:" prefix.)"""
        self._write('%s\r\n' % status)


    def send_headers(self):
        """Transmit headers to the client, via self._write()"""
        self.cleanup_headers()
        self.headers_sent = True
        self.send_status()
        self._write(str(self.headers))


    def result_is_file(self):
        """True if 'self.result' is an instance of 'self.wsgi_file_wrapper'"""
        wrapper = self.wsgi_file_wrapper
        return wrapper is not None and isinstance(self.result,wrapper)


    # Pure abstract methods; *must* be overridden in subclasses

    def handle_error(self):
        """Override in subclass to handle error recovery and logging"""
        # XXX this really should do something sensible by default
        raise NotImplementedError

    def _write(self,data):
        """Override in subclass to buffer data for send to client"""
        raise NotImplementedError

    def _flush(self):
        """Override in subclass to force sending of recent '_write()' calls"""
        raise NotImplementedError

    def get_stdin(self):
        """Override in subclass to return suitable 'wsgi.input'"""
        raise NotImplementedError

    def get_stderr(self):
        """Override in subclass to return suitable 'wsgi.errors'"""
        raise NotImplementedError

    def add_cgi_vars(self):
        """Override in subclass to insert CGI variables in 'self.environ'"""
        raise NotImplementedError















class BaseCGIHandler(BaseHandler):
    """CGI-like systems using input/output/error streams and environ mapping

    Usage::

        handler = BaseCGIHandler(inp,out,err,env)
        handler.run(app)

    This handler class is useful for gateway protocols like ReadyExec and
    FastCGI, that have usable input/output/error streams and an environment
    mapping.  It's also the base class for CGIHandler, which just uses
    sys.stdin, os.environ, and so on.

    The constructor also takes keyword arguments 'multithread' and
    'multiprocess' (defaulting to 'True' and 'False' respectively) to control
    the configuration sent to the application.
    """

    wsgi_multithread = False
    wsgi_multiprocess = True

    def __init__(self,stdin,stdout,stderr,environ,
        multithread=True, multiprocess=False
    ):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.base_env = environ
        self.wsgi_multithread = multithread
        self.wsgi_multiprocess = multiprocess

    def get_stdin(self):
        return self.stdin

    def get_stderr(self):
        return self.stderr

    def add_cgi_vars(self):
        self.environ.update(self.base_env)


    def _write(self,data):
        self.stdout.write(data)
        self._write = self.stdout.write

    def _flush(self):
        self.stdout.flush()
        self._flush = self.stdout.flush

    def send_status(self):
        self._write('Status: %s\r\n' % self.status)


class CGIHandler(BaseCGIHandler):
    """CGI-based invocation via sys.stdin/stdout/stderr and os.environ

    The difference between this class and BaseCGIHandler is that it always
    uses 'wsgi.last_call' of 'True', 'wsgi.multithread' of 'False', and
    'wsgi.multiprocess' of 'True'.  It does not take any initialization
    parameters, but always uses 'sys.stdin', 'os.environ', and friends.

    If you need to override any of these parameters, use BaseCGIHandler
    instead.
    """

    wsgi_last_call = True

    def __init__(self):
        BaseCGIHandler.__init__(
            self, sys.stdin, sys.stdout, sys.stderr, dict(os.environ.items()),
            multithread=False, multiprocess=True
        )










