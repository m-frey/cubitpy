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
    hex8sh = 6

    def get_string(self):
        """Get the string representation of this element type."""
        if self.value == self.hex8:
            return 'hex8'
        elif self.value == self.hex20:
            return 'hex20'
        elif self.value == self.hex27:
            return 'hex27'
        elif self.value == self.tet4:
            return 'tet4'
        elif self.value == self.tet10:
            return 'tet10'

    def get_cubit_names(self):
        """
        Get the strings that are needed to mesh and describe this element in
        cubit.
        """

        # Get the element type parameters.
        if (self.value == self.hex8 or self.value == self.hex8sh):
            cubit_scheme = 'Auto'
            cubit_element_type = 'HEX8'
        elif self.value == self.hex20:
            cubit_scheme = 'Auto'
            cubit_element_type = 'HEX20'
        elif self.value == self.hex27:
            cubit_scheme = 'Auto'
            cubit_element_type = 'HEX27'
        elif self.value == self.tet4:
            cubit_scheme = 'Tetmesh'
            cubit_element_type = 'TETRA4'
        elif self.value == self.tet10:
            cubit_scheme = 'Tetmesh'
            cubit_element_type = 'TETRA10'
        else:
            raise ValueError('Got wrong element type {}!'.format(self.value))

        return cubit_scheme, cubit_element_type

    def get_baci_name(self):
        """Get the name of this element in baci."""

        # Get the element type parameters.
        if self.value == self.hex8:
            return 'SOLIDH8'
        elif self.value == self.hex20:
            return 'SOLIDH20'
        elif self.value == self.hex27:
            return 'SOLIDH27'
        elif self.value == self.tet4:
            return 'SOLIDT4'
        elif self.value == self.tet10:
            return 'SOLIDT10'
        elif self.value == self.hex8sh:
            return 'SOLIDSH8'
        else:
            raise ValueError('Got wrong element type {}!'.format(self.value))

    def get_default_baci_description(self):
        """
        Get the default text for the description in baci after the material
        string.
        """

        # Get the element type parameters.
        if self.value == self.hex8:
            return 'KINEM nonlinear EAS none'
        elif (self.value == self.hex20
                or self.value == self.hex27
                or self.value == self.tet4
                or self.value == self.tet10):
            return 'KINEM nonlinear'
        elif self.value == self.hex8sh:
            return 'KINEM nonlinear EAS none ANS none THICKDIR auto'
        else:
            raise ValueError('Got wrong element type {}!'.format(self.value))


class BoundaryConditionType(IntEnum):
    """Enum for boundary conditions types."""
    dirichlet = 1
    neumann = 2
    beam_to_solid_volume_meshtying = 3
    beam_to_solid_surface_meshtying = 4

    def get_dat_bc_section_header(self, geometry_type):
        """
        Get the header string for the boundary condition input section in the
        dat file.
        """

        if self.value == self.dirichlet or self.value == self.neumann:
            if self.value == self.dirichlet:
                self_string = 'DIRICH'
            else:
                self_string = 'NEUMANN'

            return 'DESIGN {} {} CONDITIONS'.format(
                geometry_type.get_dat_bc_section_string(),
                self_string
                )
        elif (self.value == self.beam_to_solid_volume_meshtying and
                geometry_type == GeometryType.volume):
            return 'BEAM INTERACTION/BEAM TO SOLID VOLUME MESHTYING VOLUME'
        elif (self.value == self.beam_to_solid_surface_meshtying and
                geometry_type == GeometryType.surface):
            return 'BEAM INTERACTION/BEAM TO SOLID SURFACE MESHTYING SURFACE'

        raise ValueError('No implemented case for {} and {}!'.format(
            self.value, geometry_type))
