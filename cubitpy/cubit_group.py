# -*- coding: utf-8 -*-
"""
This file contains a class to represent groups in cubit.
"""

# Import CubitPy stuff.
from . import cupy, CubitObject


class CubitGroup(object):
    """
    This object helps to represent groups in cubit.
    """

    def __init__(self, cubit, name, add_value=None):
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
        self.cubit = cubit

        if cubit.get_id_from_name(name) == 0:
            # If the group does not exist, create id.
            new_group_id = cubit.create_new_group()
            cubit.cmd("group {} rename '{}'".format(new_group_id, name))
        else:
            raise ValueError('The given group "{}" already exists!'.format(
                self.name))

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
            self.cubit.cmd('group "{}" {}'.format(self.name, add_value))
        elif isinstance(add_value, CubitObject):
            self.cubit.add_entity_to_group(
                self.get_cubit_id(),
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
            raise TypeError('There has to be exactly one geometry type.')

        # Return the type.
        return group_types[0]

    def get_cubit_id(self):
        """Get the id of this group in cubit."""
        cubit_id = self.cubit.get_id_from_name(self.name)
        if cubit_id == 0:
            raise ValueError('Could not find a cubit item with the '
                + 'name {}!'.format(self.name))
        return cubit_id

    def get_group_items(self, geometry_type):
        """
        Get a list of all items in the group for the given geometry_type.
        """

        group_id = self.get_cubit_id()
        if geometry_type == cupy.geometry.vertex:
            return self.cubit.get_group_vertices(group_id)
        elif geometry_type == cupy.geometry.curve:
            return self.cubit.get_group_curves(group_id)
        elif geometry_type == cupy.geometry.surface:
            return self.cubit.get_group_surfaces(group_id)
        elif geometry_type == cupy.geometry.volume:
            return self.cubit.get_group_volumes(group_id)
        else:
            raise TypeError('Wrong geometry type.')

    def get_geometry_dict(self):
        """
        Return a dictionary where the keys are the geometry types and the
        values are lists of the items of that geometry type in the group.
        """

        group_items = {}
        for geometry_type in cupy.geometry:
            group_items[geometry_type] = self.get_group_items(geometry_type)
        return group_items

    def id(self):
        """Return the string with all ids of the types in this object."""
        id_list = self.get_group_items(self.get_geometry_type())
        return ' '.join(map(str, id_list))
    