import os

from . import _libheif_cffi

from .constants import *
from .reader import *
from .writer import *

# https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyheif
# https://pypi.org/project/pyheif/

__version__ = '0.6.0'


def libheif_version():
    version = _libheif_cffi.lib.heif_get_version()
    version = _libheif_cffi.ffi.string(version).decode()
    return version
