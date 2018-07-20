

# Python modules.
import sys


import os

def out(string):
    os.system('echo "{}" > /dev/pts/20'.format(string))
out('\n')

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


# Dictionary with all objects created by cubit and cubit itself.
cubit_objects = {}

# First receive is the initialization of cubit.
# init = ['init', cubit_path, [args]]
init = channel.receive()
if not init[0] == 'init':
    raise ValueError('First call must be init!')
if not len(init) == 3:
    raise ValueError('Three arguments must be given to init!')

# Load cubit.
sys.path.append(init[1])
import cubit
cubit.init(init[2])
cubit_objects[id(cubit)] = cubit
channel.send(object_to_id(cubit))

# Wait for input.
while 1:

    # Get input from python3.
    receive = channel.receive()

    # Break the connection.
    if receive is None:
        break


    # Input must always be of length 3.
    if not len(receive) == 3:
        raise ValueError('Input given not of length 3!')

    # Check if object given is valid cubit object.
    if receive[0] == 'isinstance':

        compare_object = cubit_objects[string_to_id(receive[1])]
        
        if (receive[2] == 'vertex'):
            channel.send(isinstance(compare_object, cubit.Vertex))
        elif (receive[2] == 'curve'):
            channel.send(isinstance(compare_object, cubit.Curve))
        elif (receive[2] == 'surface'):
            channel.send(isinstance(compare_object, cubit.Surface))
        elif (receive[2] == 'volume'):
            channel.send(isinstance(compare_object, cubit.Volume))
        else:
            raise TypeError('Wrong type {} given!'.format(receive[2]))
        
        
    elif string_to_id(receive[0]) in cubit_objects.keys():
        call_object = cubit_objects[string_to_id(receive[0])]
        
        
        # Function name for cubit.
        function = receive[1]

        # Get the function arguments.
        args = []
        for item in receive[2]:
            item_id = string_to_id(item)
            if item_id is None:
                args.append(item)
            else:
                args.append(cubit_objects[item_id])
        
        # Call the function.
        obj = call_object.__getattribute__(function)(*args)

        # Return the objects.
        if (obj is None) or isinstance(obj, str) or isinstance(obj, int) or isinstance(obj, float):
            channel.send(obj)
        else:
            # Store the object locally and return the id.
            if isinstance(obj, tuple):
                return_obj = []
                for item in obj:
                    if (item is None) or isinstance(item, str) or isinstance(item, int) or isinstance(item, float):
                        return_obj.append(item)
                    else:
                        cubit_objects[id(item)] = item
                        return_obj.append(object_to_id(item))
            else:
                cubit_objects[id(obj)] = obj
                return_obj = object_to_id(obj)
            channel.send(return_obj)

        
        
    else:
        raise ValueError('Wrong cubit object given!')


# Send EOF.
channel.send('EOF')













