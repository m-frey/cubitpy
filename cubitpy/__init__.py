# -*- coding: utf-8 -*-
"""
This module is a wrapper around the python interface of cubit.
"""

# Python modules.
import sys

# Cubit wrapper.
if (sys.version_info > (3, 0)):
    # Python is Python 3.
    from .cubit_wrapper3 import CubitConnect, CubitObject, Cubit

# Global object.
from .cubitpy import cupy, CubitPy

# Define the itCouplingems that will be exported by default.
__all__ = [
    # cubit options.
    'cupy',
    # Cubit object.
    'CubitPy'
    ]
