"""
This script gets called with python2 and loads the cubit module. With the
package execnet (in python3) a connection is established between the two
different python interpreters and data and commands can be exchanged. The
exchange happens in a serial matter, items are sent to this script, and results
are sent back, until None is sent. If cubit creates a cubit object it is saved
in a dictionary in this script, with the key beeing the id of the object. The
python3 interpreter only knows the id of this object and can pass it to this
script to call a function on it or use it as an argument.
"""

# Python modules.
import sys
import os


# Cubit constants.
cubit_vertex = 'cubitpy_vertex'
cubit_curve = 'cubitpy_curve'
cubit_surface = 'cubitpy_surface'
cubit_volume = 'cubitpy_volume'


# Default parameters
parameters = {}


def out(string):
    """
    The print version does over different interpreters, so this function prints
    strings to an active console. Insert the path of your console to get the
    right output.
    To get the current path of your console type: tty
    """

    if 'tty' in parameters.keys():
        out_console = parameters['tty']
    else:
        out_console = '/dev/pts/18'
    os.system('echo "{}" > {}'.format(string, out_console))


def is_base_type(obj):
    """
    Check if the object is of a base type that does not need conversion for the
    connection between python2 and python3.
    """
    if (isinstance(obj, str) or isinstance(obj, int) or isinstance(obj, float)
            or isinstance(obj, type(None))
            ):
        return True
    else:
        return False


def is_cubit_type(obj):
    """Check if the object is of a cubit base."""
    if (isinstance(obj, cubit.Body) or isinstance(obj, cubit.Vertex)
            or isinstance(obj, cubit.Curve) or isinstance(obj, cubit.Surface)
            or isinstance(obj, cubit.Volume)
            ):
        return True
    else:
        return False


# All cubit items that are created are stored in this dictionary. The keys are
# the unique object ids. For now no items are deleted if the GC deletes them in
# python3, there is a check that not too many items are in this dictionary.
cubit_objects = {}


# The first call are parameters needed in this script.
parameters = channel.receive()
channel.send(None)
if not isinstance(parameters, dict):
    raise TypeError('The first item should be a dictionary. '
        + 'Got {}!\nparameters={}'.format(type(parameters), parameters))

# Add paths to sys and load utility functions and cubit.
dir_name = os.path.dirname(parameters['__file__'])
sys.path.append(dir_name)
sys.path.append(parameters['cubit_path'])

from cubit_wrapper_utility import object_to_id, string_to_id
import cubit


# The second call is the initialization call for cubit.
# init = ['init', cubit_path, [args]]
init = channel.receive()
if not init[0] == 'init':
    raise ValueError('The second call must be init!')
if not len(init) == 2:
    raise ValueError('Two arguments must be given to init!')
cubit.init(init[1])
cubit_objects[id(cubit)] = cubit
channel.send(object_to_id(cubit))


# Now start an endless loop (until None is sent) and perform the cubit
# functions.
while 1:

    # Get input from python3.
    receive = channel.receive()

    # If None is sent, break the connection and exit.
    if receive is None:
        break

    # The first (string) argument decides that functionality will be performed.
    # object_id: call a method on a cubit object, with parameters
    #       ['object_id', 'method', ['parameters']]
    # isinstance: Check if the cubit object is of a cerain instance.

    if not isinstance(receive[0], str):
        raise TypeError('The first item given to python2 must be of type str! '
            + 'Got {}!'.format(type(receive[0])))

    elif string_to_id(receive[0]) is not None:
        # The first item is an id for a cubit object. Call a method on this
        # object.

        # Check the length of the cubit_objects dictionary and return an error
        # if it gets very long. Then maybe think about passing delete functions
        # from python3.
        if len(cubit_objects) > 10000:
            raise OverflowError(
                'The cubit_objects has {} items, that is too much!'.format(
                    len(cubit_objects)))

        # Get object and function name.
        call_object = cubit_objects[string_to_id(receive[0])]
        function = receive[1]

        # Get the function arguments. It is checked if one of the arguments is
        # an cubit object.
        args = []
        for item in receive[2]:
            item_id = string_to_id(item)
            if item_id is None:
                args.append(item)
            else:
                args.append(cubit_objects[item_id])

        # Call the function.
        cubit_return = call_object.__getattribute__(function)(*args)

        # Check what to return.
        if is_base_type(cubit_return):
            # The return item is a string, integer or float.
            channel.send(cubit_return)

        elif isinstance(cubit_return, tuple):
            # A tuple was returned, loop over each entry and check its type.
            return_list = []
            for item in cubit_return:
                if is_base_type(item):
                    return_list.append(item)
                elif is_cubit_type(item):
                    cubit_objects[id(item)] = item
                    return_list.append(object_to_id(item)) 
                else:
                    raise TypeError('Expected string, int, float or cubit '
                        + 'object! Got {}!'.format(item))
            channel.send(return_list)

        elif is_cubit_type(cubit_return):
            # Store the object locally and return the id.
            cubit_objects[id(cubit_return)] = cubit_return
            channel.send(object_to_id(cubit_return))

        else:
            raise TypeError('Expected string, int, float, cubit object or '
                + 'tuple! Got {}!'.format(cubit_return))

    elif receive[0] == 'isinstance':
        # Compare the second item with a predefined cubit class.
        compare_object = cubit_objects[string_to_id(receive[1])]

        if (receive[2] == cubit_vertex):
            channel.send(isinstance(compare_object, cubit.Vertex))
        elif (receive[2] == cubit_curve):
            channel.send(isinstance(compare_object, cubit.Curve))
        elif (receive[2] == cubit_surface):
            channel.send(isinstance(compare_object, cubit.Surface))
        elif (receive[2] == cubit_volume):
            channel.send(isinstance(compare_object, cubit.Volume))
        else:
            raise ValueError('Wrong compare type given! Expected vertex, '
                + 'curve, surface or volume, got{}'.format(receive[2]))

    elif receive[0] == 'get_methods':
        # Return a list with all callable methods of this object.
        cubit_object = cubit_objects[string_to_id(receive[1])]
        channel.send([
            method_name for method_name in dir(cubit_object)
            if callable(getattr(cubit_object, method_name))
            ])

    else:
        raise ValueError('The case of "{}" is not implemented!'.format(
            receive[0]))


# Send EOF.
channel.send('EOF')
