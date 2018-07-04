# -*- coding: utf-8 -*-
"""
This module is a wrapper around the python interface of cubit.
"""

# Global object.
from .cubitpy import cupy, CubitPy

# Define the itCouplingems that will be exported by default.
__all__ = [
    # cubit options.
    'cupy',
    # Cubit object.
    'CubitPy'
    ]
