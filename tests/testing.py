# -*- coding: utf-8 -*-
"""
This script is used to test the functionality of the cubitpy module.
"""

# Python imports.
import unittest
import os
import subprocess
import numpy as np

# Cubitpy imports.
from cubitpy import CubitPy

# Define the testing paths.
testing_path = os.path.abspath(os.path.dirname(__file__))
testing_input = os.path.join(testing_path, 'input-files-ref')
testing_temp = os.path.join(testing_path, 'testing-tmp')


def check_tmp_dir():
    """Check if the temp directory exists, if not create it."""
    if not os.path.exists(testing_temp):
        os.makedirs(testing_temp)


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

    def create_block(self, cubit):
        """Create a block with cubit."""

        # Set head
        cubit.head = '''
            //stuff for head
            // other stuff for head
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

        # Create the dat file for the solid.
        check_tmp_dir()
        dat_file = os.path.join(testing_temp, 'test_create_block_cubitpy.dat')
        cubit.create_dat(dat_file)

        # Compare with the ref file.
        ref_file = os.path.join(testing_input, 'test_create_block_ref.dat')
        with open(dat_file, 'r') as text_file:
            string1 = text_file.read()
        with open(ref_file, 'r') as text_file:
            string2 = text_file.read()
        self.assertTrue(
            compare_strings(string1, string2),
            'test_create_block'
            )

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


if __name__ == '__main__':
    unittest.main()
