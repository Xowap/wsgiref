from distutils.core import Distribution as _Distribution

from setuptools.command.build_py import build_py

class Distribution(_Distribution):

    # 'get_dependencies' command
    requires = ()

    # 'test' command
    test_module = None

    # 'install_pkg_data' command
    package_data = ()


    def __init__ (self, attrs=None):
        _Distribution.__init__(self,attrs)
        self.cmdclass.setdefault('build_py',build_py)
        # XXX self.cmdclass.setdefault('build',build)

    def has_pkg_data(self):
        return self.package_data

