# -*- coding: utf-8 -*-
"""
This module contains ENums for types used in cubitpy as well as functions to
convert them to strings for cubit or baci commands or the python2 wrapper.
"""

# Python imports.
from enum import IntEnum


class GeometryType(IntEnum):
    """Enum for geometry types."""
    vertex = 1
    curve = 2
    surface = 3
    volume = 4


class FiniteElementObjects(IntEnum):
    """Enum for finite element objects."""
    hex_elements = 1
    tet_elements = 2
    face = 3
    triangle = 4
    edge = 5
    node = 6
