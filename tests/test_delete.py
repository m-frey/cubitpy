# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# CubitPy: A cubit utility funcitons and a cubit wrapper for python3.
#
# Copyright (c) 2021 Ivo Steinbrecher
#                    Institute for Mathematics and Computer-Based Simulation
#                    Universitaet der Bundeswehr Muenchen
#                    https://www.unibw.de/imcs-en
#
# TODO: Add license.
# -----------------------------------------------------------------------------
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
