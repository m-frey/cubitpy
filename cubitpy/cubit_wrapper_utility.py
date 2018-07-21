# -*- coding: utf-8 -*-
"""
Utility functions that can be used in python2 and python3.
"""


def object_to_id(obj):
    """Return a string id of obj."""
    return 'cp2t3id_' + str(id(obj))


def string_to_id(string):
    """Return the id from a id string."""
    if not isinstance(string, str):
        return None
    if string.startswith('cp2t3id_'):
        return int(string[8:])
    else:
        return None
