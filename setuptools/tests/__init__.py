from unittest import TestSuite, TestCase, makeSuite
import distutils.core, distutils.cmd
from distutils.errors import DistutilsOptionError
import setuptools, setuptools.dist

def makeSetup(**args):
    """Return distribution from 'setup(**args)', without executing commands"""
    distutils.core._setup_stop_after = "commandline"
    try:
        return setuptools.setup(**args)
    finally:
        distutils.core_setup_stop_after = None


class DistroTests(TestCase):

    def testDistro(self):
        self.failUnless(isinstance(makeSetup(),setuptools.dist.Distribution))























class TestCommandTests(TestCase):

    def testTestIsCommand(self):
        test_cmd = makeSetup().get_command_obj('test')
        self.failUnless(isinstance(test_cmd, distutils.cmd.Command))

    def testLongOptSuiteWNoDefault(self):
        ts1 = makeSetup(script_args=['test','--test-suite=foo.tests.suite'])
        ts1 = ts1.get_command_obj('test')
        ts1.ensure_finalized()
        self.assertEqual(ts1.test_suite, 'foo.tests.suite')

    def testDefaultSuite(self):
        ts2 = makeSetup(test_suite='bar.tests.suite').get_command_obj('test')
        ts2.ensure_finalized()
        self.assertEqual(ts2.test_suite, 'bar.tests.suite')

    def testDefaultWModuleOnCmdLine(self):
        ts3 = makeSetup(
            test_suite='bar.tests',
            script_args=['test','-m','foo.tests']
        ).get_command_obj('test')
        ts3.ensure_finalized()
        self.assertEqual(ts3.test_module, 'foo.tests')
        self.assertEqual(ts3.test_suite,  'foo.tests.test_suite')

    def testConflictingOptions(self):
        ts4 = makeSetup(
            script_args=['test','-m','bar.tests', '-s','foo.tests.suite']
        ).get_command_obj('test')
        self.assertRaises(DistutilsOptionError, ts4.ensure_finalized)

    def testNoSuite(self):
        ts5 = makeSetup().get_command_obj('test')
        ts5.ensure_finalized()
        self.assertEqual(ts5.test_suite, None)
        




testClasses = (DistroTests, TestCommandTests)

def test_suite():
    return TestSuite([makeSuite(t,'test') for t in testClasses])
    




































