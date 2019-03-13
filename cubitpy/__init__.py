# -*- coding: utf-8 -*-
"""
This module is a wrapper around the python interface of cubit.
"""

# Python modules.
import sys

# Global options for cubitpy.
from .conf import cupy

# Global object.
from .cubitpy import CubitPy

# Define the itCouplingems that will be exported by default.
__all__ = [
    # cubit options.
    'cupy',
    # Cubit objects.
    'CubitPy'
    ]
