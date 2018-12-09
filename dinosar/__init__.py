"""Dinosar."""

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

__all__ = ['archive', 'cloud', 'isce', 'output']

from . import archive, cloud, isce, output
