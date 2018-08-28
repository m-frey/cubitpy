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

    @staticmethod
    def get_default_paths(name, throw_error=True):
        """Look for and return a path to cubit or pre_exodus."""

        if name == 'cubit':
            default_paths = [
                ['/opt/cubit-13.2/bin', os.path.isdir],
                ['/rzhome/nas/compsim/opt/cubit-13.2/bin', os.path.isdir]
                ]
        elif name == 'pre_exodus':
            default_paths = [
                ['/home/ivo/baci/work/release/pre_exodus', os.path.isfile],
                ['/hdd/gitlab-runner/cc603775/baci/pre_exodus', os.path.isfile]
                ]
        else:
            raise ValueError('Type {} not implemented!'.format(name))

        # Check which path exists.
        for [path, function] in default_paths:
            if function(path):
                return path
        else:
            if throw_error:
                raise ValueError('Path for {} not found!'.format(name))
            else:
                return None


# Global object with options for cubitpy.
cupy = CubitOptions()
