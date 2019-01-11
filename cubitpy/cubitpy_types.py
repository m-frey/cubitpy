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

    def get_cubit_string(self):
        """Return the string that represents this item in cubit."""

        if self.value == self.vertex:
            return 'vertex'
        elif self.value == self.curve:
            return 'curve'
        elif self.value == self.surface:
            return 'surface'
        elif self.value == self.volume:
            return 'volume'

    def get_dat_bc_section_string(self):
        """
        Return the string that represents this item in a dat file section.
        """

        if self.value == self.vertex:
            return 'POINT'
        elif self.value == self.curve:
            return 'LINE'
        elif self.value == self.surface:
            return 'SURF'
        elif self.value == self.volume:
            return 'VOL'


class FiniteElementObject(IntEnum):
    """Enum for finite element objects."""
    hex_elements = 1
    tet_elements = 2
    face = 3
    triangle = 4
    edge = 5
    node = 6

    def get_cubit_string(self):
        """Return the string that represents this item in cubit."""

        if self.value == self.hex_elements:
            return 'hex'
        elif self.value == self.tet_elements:
            return 'tet'
        elif self.value == self.face:
            return 'face'
        elif self.value == self.triangle:
            return 'tri'
        elif self.value == self.edge:
            return 'edge'
        elif self.value == self.node:
            return 'node'


class ElementType(IntEnum):
    """Enum for finite element shape types."""
    hex8 = 1
    hex20 = 2
    hex27 = 3
    tet4 = 4
    tet10 = 5

    def get_element_type_strings(self):
        """
        Get the strigns that represent this element type for cubit and BACI.
        """

        # Get the element type parameters.
        if self.value == self.hex8:
            cubit_scheme = 'Auto'
            cubit_element_type = 'HEX8'
            baci_element_type = 'SOLIDH8'
            baci_dat_string = 'EAS none'
        elif self.value == self.hex20:
            cubit_scheme = 'Auto'
            cubit_element_type = 'HEX20'
            baci_element_type = 'SOLIDH20'
            baci_dat_string = ''
        elif self.value == self.hex27:
            cubit_scheme = 'Auto'
            cubit_element_type = 'HEX27'
            baci_element_type = 'SOLIDH27'
            baci_dat_string = ''
        elif self.value == self.tet4:
            cubit_scheme = 'Tetmesh'
            cubit_element_type = 'TETRA4'
            baci_element_type = 'SOLIDT4'
            baci_dat_string = ''
        elif self.value == self.tet10:
            cubit_scheme = 'Tetmesh'
            cubit_element_type = 'TETRA10'
            baci_element_type = 'SOLIDT10'
            baci_dat_string = ''

        return cubit_scheme, cubit_element_type, baci_element_type, \
            baci_dat_string


class BoundaryConditionType(IntEnum):
    """Enum for boundary conditions types."""
    dirichlet = 1
    neumann = 2

    def get_dat_bc_section_header(self, geometry_type):
        """
        Get the header string for the boundary condition input section in the
        dat file.
        """

        if self.value == self.dirichlet:
            self_string = 'DIRICH'
        else:
            self_string = 'NEUMANN'

        return 'DESIGN {} {} CONDITIONS'.format(
            geometry_type.get_dat_bc_section_string(),
            self_string
            )
