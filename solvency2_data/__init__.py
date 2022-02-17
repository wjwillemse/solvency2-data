# -*- coding: utf-8 -*-

"""Top-level package for solvency2-data."""

__version__ = "0.1.19"

from .rfr import *
from .eiopa_data import get, refresh
from .util import set_config
from .smith_wilson import *
from .alternative_extrapolation import *