# -*- coding: utf-8 -*-
"""
Utility functions that can be used in python2 and python3.
"""

import os


def object_to_id(obj):
    """
    Return list representing the cubit object. The first entry is the id of
    the object, the second entry is the string representation."""
    return [
        'cp2t3id_' + str(id(obj)),
        str(obj)
        ]


def cubit_item_to_id(cubit_data_list):
    """Return the id from a cubit data list."""
    if not isinstance(cubit_data_list, list):
        return None
    if not isinstance(cubit_data_list[0], str):
        return None
    if cubit_data_list[0].startswith('cp2t3id_'):
        return int(cubit_data_list[0][8:])
    else:
        return None


def is_base_type(obj):
    """
    Check if the object is of a base type that does not need conversion for the
    connection between python2 and python3.
    """
    if (isinstance(obj, str) or isinstance(obj, int) or isinstance(obj, float)
            or isinstance(obj, type(None))):
        return True
    else:
        return False


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
