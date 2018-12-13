# -*- coding: utf-8 -*-
"""
Test if the last element is deleted correctly.
"""

# Import python modules.
import os, sys

# Define the testing paths.
testing_path = os.path.abspath(os.path.dirname(__file__))

# Set path to find cubitpy.
sys.path.insert(0, os.path.abspath(os.path.join(testing_path, '..')))

# Import cubit module.
from cubitpy import CubitPy

# Initialize cubit
cubit = CubitPy()

# Create cylinder.
cylinder = cubit.cylinder(1, 1, 1, 1)

# Set the mesh size.
for curve in cylinder.curves():
    cubit.set_line_interval(curve, 10)
cubit.cmd('surface 1 size 0.5')

# Mesh the geometry.
cylinder.volumes()[0].mesh()
