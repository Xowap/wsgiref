import distutils.core, setuptools.command

# XXX from deps import Dependency, Distro

__all__ = ['setup', ] # XXX Dependency, Distro


def setup(**attrs):
    from setuptools.dist import Distribution
    attrs.setdefault("distclass",Distribution)   
    return distutils.core.setup(**attrs)

