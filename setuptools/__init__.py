"""Extensions to the 'distutils' for large or complex distributions"""

import distutils.core, setuptools.command
from setuptools.dist import Distribution, Feature
from distutils.core import Command, Extension

__all__ = [
    'setup', 'Distribution', 'Feature', 'Command', 'Extension'
]


def setup(**attrs):

    """Do package setup

    This function takes the same arguments as 'distutils.core.setup()', except
    that the default distribution class is 'setuptools.dist.Distribution'.  See
    that class' documentation for details on the new keyword arguments that it
    makes available via this function.
    """

    attrs.setdefault("distclass",Distribution)
    return distutils.core.setup(**attrs)

