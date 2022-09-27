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
Implements functions that create geometries in cubit.
"""

# Import cubitpy stuff.
from . import cupy


def create_parametric_curve(cubit, f, interval, n_segments=10, delete_points=True):
    """
    Create a parametric curve in space.

    Args
    ----
    cubit: Cubit
        Link to the main cubit object.
    f: function(t)
        Parametric function of a single parameter t. Maps the parameter to a
        point in R3.
    interval: [t_start, t_end]
        Start and end values for the parameter coordinate.
    n_segments: int
        Number of segments for the interval.#
    delete_points: bool
        If the created vertices should be kept or should be deleted.
    """

    # Create the vertices along the curve.
    parameter_points = [
        interval[0] + i * (interval[1] - interval[0]) / float(n_segments)
        for i in range(n_segments + 1)
    ]
    vertices = [cubit.create_vertex(*f(t)) for t in parameter_points]
    vertices_ids = [str(vertex.id()) for vertex in vertices]
    cubit.cmd(
        "create curve spline vertex {} {}".format(
            " ".join(vertices_ids), ("delete" if delete_points else "")
        )
    )
    return cubit.curve(cubit.get_last_id(cupy.geometry.curve))


def create_parametric_surface(
    cubit, f, interval, n_segments=[10, 10], delete_curves=True, delete_points=True
):
    """
    Create a parametric surface in space.

    Args
    ----
    cubit: Cubit
        Link to the main cubit object.
    f: function(u, v)
        Parametric function of two surface parameters u and v. Maps a single
        set of parameters (u, v) to a point in R3.
    interval: [[u_start, u_end], [v_start, v_end]]
        Start and end values for the parameter coordinate.
    n_segments: [int, int]
        Number of segments for the interval in u and v.
    delete_curves: bool
        If the created curves should be kept or should be deleted.
    delete_points: bool
        If the created vertices should be kept or should be deleted.
    """

    # Loop over the parameter coordinates dimension.
    curves = [[], []]
    for dim in range(2):

        # Get the constant values for the other parameter coordinate in this
        # direction.
        other_dim = 1 - dim
        parameter_points = [
            interval[other_dim][0]
            + i
            * (interval[other_dim][1] - interval[other_dim][0])
            / float(n_segments[other_dim])
            for i in range(n_segments[other_dim] + 1)
        ]

        # Create all curves along this parameter coordinate.
        for point in parameter_points:

            def f_temp(t):
                """
                Temporary function that is evaluated at a constant value of one
                of the two parameter coordinates.
                """
                if dim == 0:
                    return f(t, point)
                else:
                    return f(point, t)

            curves[dim].append(
                create_parametric_curve(
                    cubit,
                    f_temp,
                    interval[dim],
                    n_segments=n_segments[dim],
                    delete_points=delete_points,
                )
            )

    # Create the surface.
    curve_u_ids = " ".join([str(curve.id()) for curve in curves[0]])
    curve_v_ids = " ".join([str(curve.id()) for curve in curves[1]])
    cubit.cmd(
        "create surface net U curve {} V curve {} noheal".format(
            curve_u_ids, curve_v_ids
        )
    )

    if delete_curves:
        for id_string in [curve_u_ids, curve_v_ids]:
            cubit.cmd("delete curve {}".format(id_string))

    return cubit.surface(cubit.get_last_id(cupy.geometry.surface))
