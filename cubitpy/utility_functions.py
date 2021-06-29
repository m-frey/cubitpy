# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# CubitPy: Cubit utility funcitons and a cubit wrapper for python3
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
Utility functions for cubitpy.
"""

# Python imports.
import os


def check_environment_eclipse():
    """
    Adapt the environment path given to python by eclipse to call cubit.
    """

    # Flag if the script is run with eclipse or not. This will temporary
    # delete the python path so that the python2 interpreter does not look
    # in the wrong directories.
    # https://stackoverflow.com/questions/3248271/eclipse-using-multiple-python-interpreters-with-execnet
    # Also the console output will not be redirected to the eclipse console
    # but the path to a other console should be explicitly given if needed.

    if ('PYTHONPATH' in os.environ.keys()
            and 'pydev' in os.environ['PYTHONPATH']):
        python_path_old = os.environ['PYTHONPATH']
        python_path_new_list = []
        for item in python_path_old.split(':'):
            if (('/input' in item) or ('/cubitpy' in item)
                    or ('/meshpy' in item)):
                python_path_new_list.append(item)
        os.environ['PYTHONPATH'] = ':'.join(python_path_new_list)
        return True, python_path_old
    else:
        return False, ''
