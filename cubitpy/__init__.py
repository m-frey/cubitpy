# -*- coding: utf-8 -*-
"""
This module is a wrapper around the python interface of cubit.
"""

# Python modules.
import sys

# Global options for cubitpy.
from .conf import cupy

# Cubit wrapper is needed to use cubit in python3.
from .cubit_wrapper3 import CubitConnect, CubitObject

# Global object.
from .cubitpy import CubitPy

# Define the itCouplingems that will be exported by default.
__all__ = [
    # cubit options.
    'cupy',
    # Cubit object.
    'CubitPy'
    ]
