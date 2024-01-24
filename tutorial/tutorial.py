# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# CubitPy: Cubit utility functions and a cubit wrapper for python3
#
# MIT License
#
# Copyright (c) 2021 Ivo Steinbrecher
#                    Institute for Mathematics and Computer-Based Simulation
#                    Universitaet der Bundeswehr Muenchen
#                    https://www.unibw.de/imcs-en
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# -----------------------------------------------------------------------------
"""
This script contains a tutorial for Cubitpy, following the Cubit tutorial. Most basic functionality is covered
by this tutorial. For more information have a closer look at the test cases,
as they cover all functionality.
"""

# Meshpy modules.
import subprocess
import cubitpy


# Import cubitpy module.
from cubitpy import CubitPy, cupy
from cubitpy.mesh_creation_functions import create_brick

from meshpy import mesh


def cubitpy_tutorial(baci, output):
    # In the first step, a cubitpy object is created to connect the
    # code with the wrapper for Cubit. This also allows for direct insertion
    # of commands, which will be shown at a later stage.
    cubit = CubitPy()

    # Once the cubitpy object is initialized, we can create our first brick
    # object. For that we pass the cubitpy object, the dimensions of the brick
    # in x, y, and z directions. the type of elements for the meshing phase,
    # the meshing interval in [x, y, z] directions, and the element conditions
    # (linear or nonlinear kinematics).
    brick_1 = create_brick(cubit, 10, 10, 10, mesh=False)

    # The cube can be shown on your display using the following command
    # (You may have to click on the coordinate icon or refresh the display
    # for the item to show)
    cubit.display_in_cubit()

    # Now you must form the cylinder which will be used to cut the hole
    # from the brick. This is accomplished with the command:
    cubit.cmd("create cylinder height 12 radius 3")

    # At this point you will see both a brick and a cylinder appear
    # in the CUBIT display window.
    cubit.display_in_cubit()

    # Now, the cylinder can be subtracted from the brick to form the hole in the block.
    # Note that both original volumes are deleted in the Boolean operation and replaced
    # with a new volume (with an id of 1) which is the result of the Boolean operation Subtract .
    cubit.cmd("subtract 2 from 1")

    # Now we start meshing by setting the intervals for the brick and defining the mesh
    # size for the volume. we begin by setting an overall volume size interval.
    # Since the brick is 10 units in length on a side, this specifies that each
    # straight curve is to receive approximately 10 mesh elements.
    cubit.cmd("volume 1 size 1.0")

    # In order to better resolve the hole in the middle of the top surface,
    # we set a smaller size for the curve bounding this hole. The IDs for the
    # curves can be either obtained from the display or by selection methods
    cubit.cmd(
        """curve 15 interval size 0.5
    curve 11 interval 5"""
    )

    # Now we can begin with meshing the surface with the hole. for that we
    # define the mesh scheme by setting to pave. Again, the ID of the surface
    # is obtained from the display or selection methods
    cubit.cmd(
        """surface 11 scheme pave
    mesh surface 11"""
    )

    # We can now see the meshed surface
    # in the CUBIT display window.
    cubit.display_in_cubit()

    # The volume mesh can now be generated. Again, the first step is to specify
    # the type of meshing scheme to be used and the second step is to issue the
    # order to mesh. In certain cases, the scheme can be determined by CUBIT
    # automatically. For sweepable volumes, the automatic scheme detection
    # algorithm also identifies the source and target surfaces of the
    # sweep automatically.

    cubit.cmd(
        """volume 1 scheme auto
    mesh volume 1"""
    )

    # We can now see the meshed volume
    # in the CUBIT display window.
    cubit.display_in_cubit()

    # We can now define the boundary conditions, from supports to loading.
    # We will place a load on the top side of the cube, and fix the bottom.
    # It is worth noting that using coordinates to select the geometry
    # is preferred, as the element ID may change with different
    # versions / runs of Cubit.
    cubit.add_node_set(
        cubit.group(add_value="add surface with y_coord < -4.99"),
        name="fix",
        bc_type=cupy.bc_type.dirichlet,
        bc_description="NUMDOF 3 ONOFF 1 1 1 VAL 0 0 0 FUNCT 0 0 0 TAG monitor_reaction",
    )

    cubit.add_node_set(
        cubit.group(add_value="add surface with y_coord > 4.99 "),
        name="load",
        bc_type=cupy.bc_type.neumann,
        bc_description="NUMDOF 3 ONOFF 0 1 0 VAL 0 1E-1 0 FUNCT 0 1 0",
        geometry_type=cupy.geometry.vertex,
    )

    # We can view the created mesh along with the node sets we defined
    # earlier with the boundary conditions.
    cubit.display_in_cubit()

    # Set the head string.
    cubit.head = """
    -------------------------------------------------------------------PROBLEM TYP
    PROBLEMTYP                      Structure
    ----------------------------------------------------------------------------IO
    OUTPUT_BIN                      yes
    STRUCT_DISP                     yes
    FILESTEPS                       1000
    VERBOSITY                       Standard
    STRUCT_STRAIN                   gl
    STRUCT_STRESS                   cauchy
    OUTPUT_SPRING                   Yes
    WRITE_INITIAL_STATE             yes
    --------------------------------------------------------IO/MONITOR STRUCTURE DBC
    PRECISION_FILE                        16
    PRECISION_SCREEN                      5
    FILE_TYPE                             csv
    INTERVAL_STEPS                        1
    ---------------------------------------------------------IO/RUNTIME VTK OUTPUT
    OUTPUT_DATA_FORMAT              ascii
    INTERVAL_STEPS                  1
    EVERY_ITERATION                 no
    -----------------------------------------------IO/RUNTIME VTK OUTPUT/STRUCTURE
    OUTPUT_STRUCTURE                yes
    DISPLACEMENT                    yes
    ELEMENT_OWNER                   no
    STRESS_STRAIN                   yes
    GAUSS_POINT_DATA_OUTPUT_TYPE    none
    ----------------------------------------------------------------------SOLVER 1
    NAME                            Structure_Solver
    SOLVER                          Superlu
    ------------------------------------------------------------STRUCTURAL DYNAMIC
    INT_STRATEGY                    Standard
    DYNAMICTYP                      Statics
    PRESTRESSTOLDISP                1e-10
    RESULTSEVRY                     1
    RESTARTEVRY                     1
    TIMESTEP                        0.5
    NUMSTEP                         20
    MAXTIME                         10
    TOLDISP                         1e-10
    TOLRES                          1e-10
    LINEAR_SOLVER                   1
    NLNSOL                          fullnewton
    MAXITER                         200
    -----------------------------------------------------------STRUCT NOX/Printing
    Outer Iteration                 = Yes
    Inner Iteration                 = No
    Outer Iteration StatusTest      = No
    ---------------------------------------------------------------------MATERIALS
     MAT 1 MAT_Struct_StVenantKirchhoff  YOUNG 1.0E1  NUE 0.48 DENS 0 
    --------------------------------------------------------------------------FUNCT1
    SYMBOLIC_FUNCTION_OF_TIME t
    """

    # Write the input file.
    cubit.create_dat(output + "/CubitTutorial.dat")

    # Run Baci - get output
    subprocess.run(
        [
            baci,
            output + "/CubitTutorial.dat",
            output + "/Test",
        ]
    )


if __name__ == "__main__":
    """Execution part of script."""

    # Set your baci-release directory and you designated output directory
    baci = "/home/$USERNAME/Desktop/Baci/BuildBaci/baci-release"
    output = "/home/$USERNAME/Desktop/CubitPy/Test"

    cubitpy_tutorial(baci, output)
