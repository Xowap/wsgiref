"""Extensions to the 'distutils' for large or complex distributions"""

import distutils.core, setuptools.command
from setuptools.dist import Distribution, Feature
from setuptools.extension import Extension
from distutils.core import Command
import os.path

__all__ = [
    'setup', 'Distribution', 'Feature', 'Command', 'Extension', 'findPackages'
]


def findPackages(where='.', prefix='', append=None):
    """List all Python packages found within directory 'where'"""

    out = []
    if not append:
        append = out.append

    for name in os.listdir(where):
        fn = os.path.join(where,name)
        if (os.path.isdir(fn) and
            os.path.isfile(os.path.join(fn,'__init__.py'))
        ):
            append(prefix+name)
            findPackages(fn,prefix+name+'.',append)
    return out


def setup(**attrs):
    """Do package setup

    This function takes the same arguments as 'distutils.core.setup()', except
    that the default distribution class is 'setuptools.dist.Distribution'.  See
    that class' documentation for details on the new keyword arguments that it
    makes available via this function.
    """
    attrs.setdefault("distclass",Distribution)
    return distutils.core.setup(**attrs)

