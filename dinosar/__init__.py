"""Dinosar."""

import pkg_resources

# https://github.com/python-poetry/poetry/issues/144#issuecomment-559793020
def get_version():
    try:
        distribution = pkg_resources.get_distribution("lfelib")
    except pkg_resources.DistributionNotFound:
        return "dev"  # or "", or None
        # or try with importib.metadata (py>3.8)
        # or try reading pyproject.toml
    else:
        return distribution.version


__version__ = get_version()

__all__ = ["archive", "cloud", "isce", "output"]

from . import archive, cloud, isce, output
