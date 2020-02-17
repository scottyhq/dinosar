"""Dinosar."""

import pkg_resources
from . import archive, cloud, isce, output


# https://github.com/python-poetry/poetry/issues/144#issuecomment-559793020
def get_version():
    try:
        distribution = pkg_resources.get_distribution("dinosar")
    except pkg_resources.DistributionNotFound:
        return "pkg_resources.DistributionNotFound"
    else:
        return distribution.version


__version__ = get_version()
__all__ = ["archive", "cloud", "isce", "output"]
