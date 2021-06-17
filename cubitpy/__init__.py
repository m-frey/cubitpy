# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# CubitPy: A cubit utility funcitons and a cubit wrapper for python3.
#
# Copyright (c) 2021 Ivo Steinbrecher
#                    Institute for Mathematics and Computer-Based Simulation
#                    Universitaet der Bundeswehr Muenchen
#                    https://www.unibw.de/imcs-en
#
# TODO: Add license.
# -----------------------------------------------------------------------------
"""
This module is a wrapper around the python interface of cubit.
"""

# Python modules.
import sys

# Global options for cubitpy.
from .conf import cupy

# Global object.
from .cubitpy import CubitPy

# Utility functions.
from .cubit_utility import get_surface_center

# Define the itCouplingems that will be exported by default.
__all__ = [
    # cubit options.
    'cupy',
    # Cubit objects.
    'CubitPy'
    # Utility functions.
    'get_surface_center'
    ]
