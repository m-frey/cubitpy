# -*- coding: utf-8 -*-
"""
This file contains a class to manage finite element nodes in cubit.
"""

# Import cubitpy types.
from .cubitpy_types import FiniteElementObject


class CubitNodes(object):
    """
    This object helps to represent finite element nodes in cubit.
    """

    def __init__(self, nodes):
        """
        Initialize the object by setting the list of node IDs contained in this
        object.
        """

        if isinstance(nodes, int):
            # In case a single id is given, create a list with this single
            # entry.
            self.ids = [nodes]
        else:
            self.ids = nodes

    def get_geometry_type(self):
        """Return the finite element node type."""
        return FiniteElementObject.node

    def id(self):
        """
        Return a string with the contained IDs for the cubit command line.
        """
        return ' '.join(map(str, self.ids))
