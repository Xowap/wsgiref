from distutils.cmd import Command
from distutils.errors import DistutilsOptionError
import sys

class test(Command):

    """Command to run unit tests after installation"""

    description = "Run unit tests after installation"

    user_options = [
        ('test-module=','m', "Run 'test_suite' in specified module"),
        ('test-suite=','s',
            "Test suite to run (e.g. 'some_module.test_suite')"),
    ]

    test_suite = None
    test_module = None

    def initialize_options(self):
        pass


    def finalize_options(self):

        if self.test_suite is None:
            if self.test_module is None:
                self.test_suite = self.distribution.test_suite
            else:
                self.test_suite = self.test_module+".test_suite"
        elif self.test_module:
            raise DistutilsOptionError(
                "You may specify a module or a suite, but not both"
            )

        self.test_args = [self.test_suite]

        if self.verbose:
            self.test_args.insert(0,'--verbose')


    def run(self):

        # Install before testing
        self.run_command('install')

        if self.test_suite and not self.dry_run:
            import unittest
            unittest.main(None, None, [unittest.__file__]+self.test_args)

































