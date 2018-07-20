# -*- coding: utf-8 -*-
"""
TODO
"""


# Import python modules.
import execnet
import sys

# Import utility functions for cubitpy.
from .cubit_wrapper_utility import object_to_id, string_to_id


print(__file__)

def get_cubit_function(cubit_id):

    def cubit_function(*args, **kwargs):
        
        pass
    
    





class CubitConnect(object):
    def __init__(self, python2_file='/home/ivo/dev/cubitpy/cubitpy/cubit_wrapper2.py', interpreter='popen//python=python2.7', cubit_path='/opt/cubit-13.2/bin'):
        
        self.cubit_path = cubit_path
        
        # Set up the python2 interpreter.
        self.gw = execnet.makegateway(interpreter)
        self.gw.reconfigure(py3str_as_py2str=True)

        # Load the python2 code.
        with open(python2_file, 'r') as myfile:
            data = myfile.read()

        # Set up the connection channel.
        self.channel = self.gw.remote_exec(data)
        
        # Send parameters to the python2 interpreter
        parameters = {
            '__file__':  __file__,
            'cubit_path': cubit_path
            }
        self.channel.send(parameters)

    def init_cubit(self, arguments):

        # Initialize cubit.
        self.channel.send(['init', arguments])
        cubit_id = self.channel.receive()
        return CubitObject(self, cubit_id)
    
    def isinstance(self, obj1, geom_type):
        self.channel.send(['isinstance', obj1.cubit_id, geom_type])
        return self.channel.receive()
        
    
    def get_function(self, cubit_object, name):
        
        
        def function(*args, **kwargs):
            
            arguments = []
            for item in (args):
                if isinstance(item, CubitObject):
                    arguments.append(item.cubit_id)
                else:
                    arguments.append(item)
            print(arguments)
            self.channel.send([cubit_object.cubit_id, name, arguments])
            cubit_return = self.channel.receive()

            if cubit_return is None:
                pass
            elif isinstance(cubit_return, str):
                if string_to_id(cubit_return) is not None:
                    return CubitObject(self, cubit_return)
            elif isinstance(cubit_return, list):
                return_list = []
                for item in cubit_return:
                    if string_to_id(item) is not None:
                        return_list.append(CubitObject(self, item))
                    else:
                        return_list.append(item)
                return return_list
            else:
                print(cubit_return)
                print(type(cubit_return))
            return cubit_return
        
        return function


class CubitObject(object):
    def __init__(self, cubit_connect, cubit_id):
        
        if string_to_id(cubit_id) is None:
            raise TypeError('Wrong type {}'.format(cubit_id))
        
        self.cubit_connect = cubit_connect
        self.cubit_id = cubit_id

    
    def __getattribute__(self, key, *args, **kwargs):
        print(key)
        try:
            return object.__getattribute__(self, key, *args, **kwargs)
        except AttributeError:
            # pass to cubit connection
            return self.cubit_connect.get_function(self, key)
    
    
    def __dir__(self):
        return [1]

def print_arg(obj):

    list = (
        [method_name for method_name in dir(obj)
     if callable(getattr(obj, method_name))]
        )

    for item in list:
        print(item)


