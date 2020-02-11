# -*- coding: utf-8 -*-
"""
This file contains a class to represent groups in cubit.
"""

# Import CubitPy stuff.
from .conf import cupy
from .cubit_wrapper3 import CubitObject


class CubitGroup(object):
    """
    This object helps to represent groups in cubit.
    """

    def __init__(self, cubit, *, name=None, add_value=None):
        """
        Set up the group object.

        Args
        ----
        cubit: CubitPy
            Link to a cubitpy object.
        name: str
            Name of the group in cubit.
        add_value: str
            If this argument is given, it is added to the group.
        """

        self.name = name
        self._id = None
        self.cubit = cubit

        # Create a new group.
        self._id = cubit.create_new_group()

        # Rename it if a name was given.
        if self.name is not None:
            # Check that the name does not already exist.
            if not cubit.get_id_from_name(self.name) == 0:
                raise ValueError(
                    'The given group name "{}" already exists!'.format(
                        self.name))
            cubit.cmd("group {} rename '{}'".format(self._id, self.name))

        if add_value is not None:
            self.add(add_value)

    def add(self, add_value):
        """
        Add items to the group. This can be done in three different ways:

        Args
        ----
        add_value:
            str:
                A string that will be executed in cubit to add items.
            CubitObject.
                Add this object to the group.
            [CubitObject]:
                Add this list of cubit objects.
        """

        if isinstance(add_value, str):
            self.cubit.cmd('group {} {}'.format(self._id, add_value))
        elif isinstance(add_value, CubitObject):
            self.cubit.add_entity_to_group(
                self._id,
                add_value.id(),
                add_value.get_geometry_type().get_cubit_string())
        elif isinstance(add_value, list):
            for item in add_value:
                self.add(item)
        else:
            raise TypeError('Got wrong type {}!'.format(type(add_value)))

    def get_geometry_type(self):
        """
        Return the geometry type of this group. This only works if the group
        contains a single type of geometry.
        """

        # Get all types in the group.
        group_items = self.get_geometry_dict()
        group_types = [key for key in group_items.keys()
            if len(group_items[key]) > 0]

        # Raise an error if the group contains more than one type.
        if not len(group_types) == 1:
            raise TypeError('There has to be exactly one geometry type. '
                + 'The given group {} has the types {}!'.format(
                    self.name, group_types))

        # Return the type.
        return group_types[0]

    def get_geometry_ids(self, geometry_type):
        """
        Get a list of all items in the group for the given geometry_type.
        """

        if geometry_type == cupy.geometry.vertex:
            return self.cubit.get_group_vertices(self._id)
        elif geometry_type == cupy.geometry.curve:
            return self.cubit.get_group_curves(self._id)
        elif geometry_type == cupy.geometry.surface:
            return self.cubit.get_group_surfaces(self._id)
        elif geometry_type == cupy.geometry.volume:
            return self.cubit.get_group_volumes(self._id)
        else:
            raise TypeError('Wrong geometry type.')

    def get_geometry_objects(self, geometry_type):
        """
        Get a list of all items in the group for the given geometry_type.
        """
        all_items = self.cubit.get_items(geometry_type)
        return [all_items[i - 1] for i in self.get_geometry_ids(geometry_type)]

    def get_geometry_dict(self):
        """
        Return a dictionary where the keys are the geometry types and the
        values are lists of the items of that geometry type in the group.
        """

        group_items = {}
        for geometry_type in cupy.geometry:
            group_items[geometry_type] = self.get_geometry_ids(geometry_type)
        return group_items

    def id(self):
        """Return the string with all ids of the types in this object."""
        id_list = self.get_geometry_ids(self.get_geometry_type())
        return ' '.join(map(str, id_list))

    def __str__(self, *args, **kwargs):
        """The string representatio of a group is its name."""
        return self.name
