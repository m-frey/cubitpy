# -*- coding: utf-8 -*-
"""
This module defines a global object that manages all kind of stuff regarding
cubitpy.
"""

# Python imports.
import os


class CubitOptions(object):
    """Object for types in cubitpy."""
    def __init__(self):

        # Temporary directory for cubitpy.
        self.temp_dir = '/tmp/cubitpy'
        self.temp_log = os.path.join(self.temp_dir, 'cubitpy.log')

        # Check if temp path exits, if not create it.
        if not os.path.isdir(self.temp_dir):
            os.makedirs(self.temp_dir)#, exist_ok=True)

        # Element types
        self.vertex = 'cubitpy_vertex'
        self.curve = 'cubitpy_curve'
        self.surface = 'cubitpy_surface'
        self.volume = 'cubitpy_volume'


# Global object with options for cubitpy.
cupy = CubitOptions()
