# -*- coding: utf-8 -*-
"""
This module creates object that are used to connect between cubit in python2
and python3.
"""


# Import python modules.
import execnet
import sys
import os


# Import utility functions for cubitpy.
from .cubit_wrapper_utility import object_to_id, string_to_id


class CubitConnect(object):
    """
    This class holds a connection to a python2 interpreter and initializes
    cubit there. It is possible to send function calls to that interpreter and
    receive the output.
    """

    def __init__(self, cubit_arguments, interpreter='popen//python=python2.7',
            cubit_path='/opt/cubit-13.2/bin', debug=True):
        """
        Initialize the connection between python2 and python3. And load the
        cubit module in python2.

        Args
        ----
        cubit_arguments: [str]
            Arguments to initialize cubit with.
        interpreter: str
            Interpreter for python2 that will be used.
        cubit_path: str
            Path to the cubit executable.
        debug: bool
            If True, the path of the current console will be given to python2
            and the output from there will be redirected to the console.
        """

        # Set up the python2 interpreter.
        self.gw = execnet.makegateway(interpreter)
        self.gw.reconfigure(py3str_as_py2str=True)

        # Load the python2 code.
        python2_file = os.path.join(
            os.path.dirname(__file__),
            'cubit_wrapper2.py')
        with open(python2_file, 'r') as myfile:
            data = myfile.read()

        # Set up the connection channel.
        self.channel = self.gw.remote_exec(data)

        # Send parameters to the python2 interpreter
        parameters = {}
        parameters['__file__'] = __file__
        parameters['cubit_path'] = cubit_path

        if debug:
            # Get the current terminal path.
            import subprocess
            run = subprocess.run(['tty'], check=True, stdout=subprocess.PIPE)
            parameters['tty'] = run.stdout.decode('utf-8')

        # Send the parameters to python2
        self.send_and_return(parameters)

        # Initialize cubit.
        cubit_id = self.send_and_return(['init', cubit_arguments])
        self.cubit = CubitObject(self, cubit_id)

    def isinstance(self, cubit_object, geom_type):
        """
        Check if cubit_object is of geom_type.

        Args
        ----
        cubit_object: CubitObject
            Object to compare.
        geom_type: str
            Name of the geometry to compare (vertex, curve, surface, volume).
        """

        # Check if the object is a Cubit Object.
        if not isinstance(cubit_object, CubitObject):
            raise TypeError('Expected CubitObject, got {}!'.format(
                type(cubit_object)))

        # Compare in python2.
        return self.send_and_return(
            ['isinstance', cubit_object.cubit_id, geom_type])

    def send_and_return(self, argument_list):
        """Send arguments to python2 and collect the return values."""
        self.channel.send(argument_list)
        return self.channel.receive()

    def get_function(self, cubit_object, name):
        """
        Return a callable function that executes the method 'name' on the
        object 'cubit_object' in python2.

        Args
        ----
        cubit_object: CubitObject
            The object on which the method is called.
        name: str
            Name of the method.
        """

        def function(*args, **kwargs):
            """This function gets returned from the parent method."""

            # Check if there are cubit objects in the arguments.
            arguments = []
            for item in (args):
                if isinstance(item, CubitObject):
                    arguments.append(item.cubit_id)
                else:
                    arguments.append(item)

            # Call the method on the cubit object.
            cubit_return = self.send_and_return(
                [cubit_object.cubit_id, name, arguments])

            # Check if the return value contains cubit objects.
            if isinstance(cubit_return, str):
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

            return cubit_return

        return function


class CubitObject(object):
    """
    This class holds a link to a cubit object in python2. Methods that are
    called on this class will 'really' be called in python2.
    """

    def __init__(self, cubit_connect, cubit_id):
        """
        Initialize the object.

        Args
        ----
        cubit_connect: CubitConnect
            A link to the cubit_connec object that will be used to call
            methods.
        cubit_id: str
            The id of this object in python2.
        """

        # Check formating of cubit_id.
        if string_to_id(cubit_id) is None:
            raise TypeError('Wrong type {}'.format(cubit_id))

        self.cubit_connect = cubit_connect
        self.cubit_id = cubit_id

    def __getattribute__(self, name, *args, **kwargs):
        """
        This function gets called for each attribute in this object.
        First it is checked if the attribute exists in python3 (basic stuff),
        if not the attribute is called on python2.

        For now if an attribute is sent to python2, it is assumed that it is a
        method.
        """

        # Check if the attribute exists in python3.
        try:
            return object.__getattribute__(self, name, *args, **kwargs)
        except AttributeError:
            # Create a callable function in python2.
            return self.cubit_connect.get_function(self, name)
