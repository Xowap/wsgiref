from distutils.core import Distribution as _Distribution

from setuptools.command.build_py import build_py

class Distribution(_Distribution):

    # 'get_dependencies' command
    requires = ()

    # 'test' command
    test_suite = None

    def __init__ (self, attrs=None):
        self.package_data = {}
        _Distribution.__init__(self,attrs)
        self.cmdclass.setdefault('build_py',build_py)
        # XXX self.cmdclass.setdefault('build',build)

