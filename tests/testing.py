# -*- coding: utf-8 -*-
"""
This script is used to test the functionality of the cubitpy module.
"""

# Python imports.
import unittest
import os
import sys
import subprocess
import numpy as np

# Define the testing paths.
testing_path = os.path.abspath(os.path.dirname(__file__))
testing_input = os.path.join(testing_path, 'input-files-ref')
testing_temp = os.path.join(testing_path, 'testing-tmp')

# Set path to find cubitpy.
sys.path.insert(0, os.path.abspath(os.path.join(testing_path, '..')))

# Cubitpy imports.
from cubitpy import CubitPy, cupy
from cubitpy.mesh_creation_functions import create_brick


def check_tmp_dir():
    """Check if the temp directory exists, if not create it."""
    os.makedirs(testing_temp, exist_ok=True)


def compare_strings(string_ref, string_compare):
    """
    Compare two stings. If they are not identical open kompare and show
    differences.
    """

    # Check if the strings are equal, if not fail the test and show the
    # differences in the strings.
    name = 'cubitpy_testing'
    compare = string_ref == string_compare
    if not compare:
        check_tmp_dir()
        strings = [string_ref, string_compare]
        files = []
        files.append(os.path.join(testing_temp, '{}_ref.dat'.format(name)))
        files.append(
            os.path.join(testing_temp, '{}_compare.dat'.format(name)))
        for i, file in enumerate(files):
            with open(file, 'w') as input_file:
                input_file.write(strings[i])
        child = subprocess.Popen(
            ['kompare', files[0], files[1]], stderr=subprocess.PIPE)
        child.communicate()
    return compare


class TestCubitPy(unittest.TestCase):
    """This class tests the implementation of the CubitPy class."""

    def compare(self, cubit, name, single_precision=False):
        """
        Write create the dat file from the cubit mesh and compare to a
        reference file.

        Args
        ----
        cubit: Cubit object.
        name: str
            Name of the test case. A reference file 'name' + '_ref.dat' must
            exits in the reference file folder.
        single_precision: bool
            If the output of cubit is single or double precision.
        """

        # Create the dat file for the solid.
        check_tmp_dir()
        dat_file = os.path.join(testing_temp, name + '.dat')
        if single_precision:
            cubit.cmd('set exodus single precision on')
        cubit.create_dat(dat_file)

        # Compare with the ref file.
        ref_file = os.path.join(testing_input, name + '_ref.dat')
        with open(dat_file, 'r') as text_file:
            string1 = text_file.read()
        with open(ref_file, 'r') as text_file:
            string2 = text_file.read()
        self.assertTrue(
            compare_strings(string1, string2), name)

    def create_block(self, cubit):
        """Create a block with cubit."""

        # Set head
        cubit.head = '''
            // Header processed by cubit.
            '''

        # Dimensions of the block.
        lx, ly, lz = [0.1, 1, 10]

        # Number of elements in the directions.
        [nx, ny, nz] = [2, 4, 8]

        # Create the block.
        block = cubit.brick(lx, ly, lz)

        # Move the block.
        cubit.move(block, [0, 0, block.bounding_box()[2]])

        # Set the meshing parameters for the curves.
        for line in block.curves():
            point_on_line = line.position_from_fraction(0.5)
            tangent = np.array(line.tangent(point_on_line))
            if np.abs(np.dot(tangent, [1, 0, 0])) > 1e-5:
                cubit.set_line_interval(line, nx)
            elif np.abs(np.dot(tangent, [0, 1, 0])) > 1e-5:
                cubit.set_line_interval(line, ny)
            elif np.abs(np.dot(tangent, [0, 0, 1])) > 1e-5:
                cubit.set_line_interval(line, nz)
            else:
                raise ArithmeticError('Error')

        # Mesh the block.
        block.mesh()
        cubit.add_element_type(block.volumes()[0], 'HEX8', name='block',
            bc=['STRUCTURE',
                'MAT 1 KINEM nonlinear EAS none',
                'SOLIDH8'
                ])

        # Create node sets.
        cubit.add_node_set(block.volumes()[0], name='all')
        for i, surf in enumerate(block.surfaces()):
            normal = np.array(surf.normal_at(cubit.get_surface_center(surf)))
            if np.dot(normal, [0, 0, -1]) == 1:
                cubit.add_node_set(surf, name='fix', bc=[
                    'DESIGN SURF DIRICH CONDITIONS',
                    'NUMDOF 6 ONOFF 1 1 1 0 0 0 VAL 0.0 0.0 0.0 0.0 0.0 0.0 '
                    + 'FUNCT 0 0 0 0 0 0'])
            elif np.dot(normal, [0, 0, 1]) == 1:
                cubit.add_node_set(surf, name='load', bc=[
                    'DESIGN SURF DIRICH CONDITIONS',
                    'NUMDOF 6 ONOFF 1 1 1 0 0 0 VAL 0.0 0.0 0.0 0.0 0.0 0.0 '
                    + 'FUNCT 0 0 0 0 0 0'])
            else:
                cubit.add_node_set(surf, name='load{}'.format(i), bc=[
                    'DESIGN SURF NEUMANN CONDITIONS',
                    'NUMDOF 6 ONOFF 1 1 1 0 0 0 VAL 0.0 0.0 0.0 0.0 0.0 0.0 ' +
                    'FUNCT 0 0 0 0 0 0'])

        # Compare the input file created for baci.
        self.compare(cubit, 'test_create_block')

    def test_create_block(self):
        """
        Test the creation of a cubit block
        """

        # Initialize cubit.
        cubit = CubitPy()
        self.create_block(cubit)

    def test_create_block_multiple(self):
        """
        Test the creation of a cubit block multiple time to check that cubit
        can be reset.
        """

        # Initialize cubit.
        cubit = CubitPy()
        self.create_block(cubit)

        # Delete the old cubit object and run the function twice on the new.
        cubit = CubitPy()
        for _i in range(2):
            self.create_block(cubit)
            cubit.reset()

        # Create two object and keep them in parallel.
        cubit = CubitPy()
        cubit_2 = CubitPy()
        self.create_block(cubit)
        self.create_block(cubit_2)

    def test_element_types(self):
        """Create a curved solid in a curved solid."""

        # Initialize cubit.
        cubit = CubitPy()

        def add_arc(radius, angle):
            """Add a arc segment."""
            cubit.cmd(('create curve arc radius {} center location 0 0 0 '
                + 'normal 0 0 1 start angle 0 stop angle {}').format(
                    radius, angle))

        mesh_types = [
            ['Tetmesh', 'TETRA4', 'SOLIDT4', ''],
            ['Auto', 'HEX8', 'SOLIDH8', 'EAS none'],
            ['Tetmesh', 'TETRA10', 'SOLIDT10', ''],
            ['Auto', 'HEX20', 'SOLIDH20', ''],
            ['Auto', 'HEX27', 'SOLIDH27', '']
            ]
        for i, [scheme, string1, string2, dat_string] in enumerate(mesh_types):

            # Offset for the next volume.
            offset_point = i * 12
            offset_curve = i * 12
            offset_surface = i * 6
            offset_volume = i

            # Add two arcs.
            add_arc(1.1, 60)
            add_arc(0.9, 60)

            # Add the closing lines.
            cubit.cmd('create curve vertex {} {}'.format(2 + offset_point,
                4 + offset_point))
            cubit.cmd('create curve vertex {} {}'.format(1 + offset_point,
                3 + offset_point))

            # Create the surface.
            cubit.cmd('create surface curve {} {} {} {}'.format(
                1 + offset_curve,
                2 + offset_curve,
                3 + offset_curve,
                4 + offset_curve))

            # Create the volume.
            cubit.cmd('sweep surface {} perpendicular distance 0.2'.format(
                1 + offset_surface
                ))

            # Move the volume.
            cubit.cmd('move Volume {} x 0 y 0 z {}'.format(1 + offset_volume,
                i * 0.4))

            # Set the size and type of the elements.
            cubit.cmd('volume {} scheme {}'.format(1 + offset_volume, scheme))

            # Set mesh properties.
            cubit.cmd('volume {} size auto factor 7'.format(1 + offset_volume))
            cubit.cmd('mesh volume {}'.format(1 + offset_volume))

            # Set the element type.
            cubit.add_element_type(
                cubit.volume(1 + offset_volume),
                string1,
                name='block_' + str(i),
                bc=['STRUCTURE',
                    'MAT 1 KINEM nonlinear {}'.format(dat_string),
                    string2
                    ])

            # Add the node sets.
            cubit.add_node_set(
                cubit.surface(5 + offset_surface),
                name='fix_' + str(i),
                bc=['DESIGN SURF DIRICH CONDITIONS',
                    'NUMDOF 3 ONOFF 1 1 1 VAL 0 0 0 FUNCT 0 0 0'])

        # Set the head string.
        cubit.head = '''
            -------------------------------------------------------------FUNCT1
            COMPONENT 0 FUNCTION t
            ----------------------------------------------------------MATERIALS
            MAT 1 MAT_Struct_StVenantKirchhoff YOUNG 1.0e+09 NUE 0.3 DENS 0.0
            ------------------------------------IO/RUNTIME VTK OUTPUT/STRUCTURE
            OUTPUT_STRUCTURE                Yes
            DISPLACEMENT                    Yes
            '''

        # Compare the input file created for baci.
        self.compare(cubit, 'test_element_types', single_precision=True)

    def test_block_function(self):
        """Create a solid block with different element types."""

        # Initialize cubit.
        cubit = CubitPy()

        element_type_list = [
            cupy.element_type.hex8,
            cupy.element_type.hex20,
            cupy.element_type.hex27,
            cupy.element_type.tet4,
            cupy.element_type.tet10
            ]

        for i, element_type in enumerate(element_type_list):
            # Create the cube with factor as mesh size.
            cube = create_brick(cubit, 0.5, 0.8, 1.1,
                element_type=element_type, mesh_size=['factor', 9],
                name=str(element_type) + str(i), mesh=False,
                material='test material string')
            cubit.move(cube, [i, 0, 0])
            cube.volumes()[0].mesh()

        for i, element_type in enumerate(element_type_list):
            # Create the cube with intervals as mesh size.
            cube = create_brick(cubit, 0.5, 0.8, 1.1,
                element_type=element_type, mesh_size=['interval', 3, 2, 1],
                name=str(element_type) + str(i + 5), mesh=False,
                material='test material string')
            cubit.move(cube, [i + 5, 0, 0])
            cube.volumes()[0].mesh()

        # Compare the input file created for baci.
        self.compare(cubit, 'test_block_function', single_precision=True)

    def test_node_set_geometry_type(self):
        """Create the boundary conditions via the bc_type enum."""

        # First create the solid mesh.
        cubit = CubitPy()
        solid = create_brick(cubit, 1, 1, 1, mesh_size=['interval', 1, 1, 1])
        cubit.add_node_set(
            solid.vertices()[0],
            name='vertex',
            bc=[
                cupy.bc_type.dirichlet,
                'NUMDOF 3 ONOFF 1 1 1 VAL 0 0 0 FUNCT 0 0 1'
                ])
        cubit.add_node_set(
            solid.curves()[0],
            name='curve',
            bc=[
                cupy.bc_type.neumann,
                'NUMDOF 3 ONOFF 1 1 1 VAL 0 0 0 FUNCT 0 0 2'
                ])
        cubit.add_node_set(
            solid.surfaces()[0],
            name='surface',
            bc=[
                cupy.bc_type.dirichlet,
                'NUMDOF 3 ONOFF 1 1 1 VAL 0 0 0 FUNCT 0 0 3'
                ])
        cubit.add_node_set(
            solid.volumes()[0],
            name='volume',
            bc=[
                cupy.bc_type.neumann,
                'NUMDOF 3 ONOFF 1 1 1 VAL 0 0 0 FUNCT 0 0 4'
                ])

        # Set the head string.
        cubit.head = '''
            ----------------------------------------------------------MATERIALS
            MAT 1 MAT_Struct_StVenantKirchhoff YOUNG 10 NUE 0.0 DENS 0.0'''

        # Compare the input file created for baci.
        self.compare(cubit, 'test_node_set_geometry_type')

    def test_groups(self):
        """
        Test that groups are handled correctly when creating node sets and
        element blocks.
        """

        # Create a solid brick.
        cubit = CubitPy()
        cubit.brick(4, 2, 1)

        # Add to group by string.
        volume = cubit.group('all_vol')
        volume.add('add volume all')

        # Add to group via string.
        surface_fix = cubit.group('fix_surf',
            'add surface in volume in all_vol with x_coord < 0')
        surface_load = cubit.group('load_surf',
            'add surface in volume in all_vol with x_coord > -1.99')

        # Add to group by CubitPy object.
        surface_load_alt = cubit.group('load_surf_alt')
        surface_load_alt.add(cubit.surface(1))
        surface_load_alt.add([cubit.surface(i) for i in [2, 3, 5, 6]])

        # Set element type.
        cubit.add_element_type(volume,
            'HEX8',
            bc=['STRUCTURE',
                'MAT 1 KINEM nonlinear EAS none',
                'SOLIDHEX8'
                ])

        # Add BCs.
        cubit.add_node_set(surface_fix,
            bc=[cupy.bc_type.dirichlet,
                'NUMDOF 3 ONOFF 1 1 1 VAL 0 0 0 FUNCT 0 0 0'])
        cubit.add_node_set(surface_load,
            bc=[cupy.bc_type.neumann,
                'NUMDOF 3 ONOFF 0 0 1 VAL 0 0 1 FUNCT 0 0 0'])
        cubit.add_node_set(surface_load_alt,
            bc=[cupy.bc_type.neumann,
                'NUMDOF 3 ONOFF 0 0 1 VAL 0 0 1 FUNCT 0 0 0'])

        # Mesh the model.
        cubit.cmd('volume {} size auto factor 8'.format(volume.id()))
        cubit.cmd('mesh {}'.format(volume))

        # Set the head string.
        cubit.head = '''
            ----------------------------------------------------------MATERIALS
            MAT 1 MAT_Struct_StVenantKirchhoff YOUNG 10 NUE 0.0 DENS 0.0'''

        # Compare the input file created for baci.
        self.compare(cubit, 'test_groups')


if __name__ == '__main__':
    unittest.main()
