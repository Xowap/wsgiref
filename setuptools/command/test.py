from distutils.cmd import Command
import sys

class test(Command):

    """Command to run unit tests after installation"""

    description = "Run unit tests after installation"

    user_options = [
        ('test-module=','m','Module to run tests from'),
    ]

    def initialize_options(self):
        self.test_module = None

    def finalize_options(self):

        if self.test_module is None:
            self.test_module = self.distribution.test_module

        self.test_args = [self.test_module+'.test_suite']

        if self.verbose:
            self.test_args.insert(0,'--verbose')

    def run(self):

        # Install before testing
        self.run_command('install')

        if not self.dry_run:
            import unittest
            unittest.main(None, None, [unittest.__file__]+self.test_args)










