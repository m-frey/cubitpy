# -*- coding: utf-8 -*-
"""
This module creates object that are used to connect between cubit in python2
and python3.
"""


# Import python modules.
import execnet
import os

# Import global options.
from . import cupy

# Import utility functions for cubitpy.
from .cubit_wrapper_utility import cubit_item_to_id, is_base_type


class CubitConnect(object):
    """
    This class holds a connection to a python2 interpreter and initializes
    cubit there. It is possible to send function calls to that interpreter and
    receive the output.
    """

    def __init__(self, cubit_arguments, interpreter='popen//python=python2.7',
            cubit_path=None):
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
        """

        if cubit_path is None:
            cubit_path = cupy.get_default_paths('cubit')

        # Flag if the script is run with eclipse or not. This will temporary
        # delete the python path so that the python2 interpreter does not look
        # in the wrong directories.
        # https://stackoverflow.com/questions/3248271/eclipse-using-multiple-python-interpreters-with-execnet
        # Also the console output will not be redirected to the eclipse console
        # but the path to a other console should be explicitly given if needed.
        if 'PYTHONPATH' in os.environ.keys():
            eclipse = 'pydev' in os.environ['PYTHONPATH']
        else:
            eclipse = False

        if eclipse:
            python_path_old = os.environ['PYTHONPATH']
            python_path_new_list = []
            for item in python_path_old.split(':'):
                if (('/input' in item) or ('/cubitpy' in item)
                        or ('/meshpy' in item)):
                    python_path_new_list.append(item)
            os.environ['PYTHONPATH'] = ':'.join(python_path_new_list)

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

        # Check if a log file was given in the cubit arguments.
        for arg in cubit_arguments:
            if arg.startswith('-log='):
                log_given = True
                break
        else:
            log_given = False

        self.log_check = False

        if not log_given:
            # Eclipse and no log given -> write the log to a temporary file and
            # check the contents after each call to cubit.
            cubit_arguments.append('-log={}'.format(cupy.temp_log))
            parameters['tty'] = cupy.temp_log
            self.log_check = True

        # Send the parameters to python2
        self.send_and_return(parameters)

        # Initialize cubit.
        cubit_id = self.send_and_return(['init', cubit_arguments])
        self.cubit = CubitObject(self, cubit_id)

        if eclipse:
            os.environ['PYTHONPATH'] = python_path_old

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

        def function(*args):
            """This function gets returned from the parent method."""

            if self.log_check:
                # Check if the log file is empty. If it is not, empty it.
                if os.stat(cupy.temp_log).st_size != 0:
                    with open(cupy.temp_log, 'w'):
                        pass

            # Check if there are cubit objects in the arguments.
            arguments = []
            for item in (args):
                if isinstance(item, CubitObject):
                    arguments.append(item.cubit_id)
                else:
                    arguments.append(item)

            # Call the method on the cubit object.
            cubit_return = self.send_and_return(
                [cubit_object.cubit_id, name, arguments]
                )

            if self.log_check:
                # Print the content of the log file.
                with open(cupy.temp_log, 'r') as log_file:
                    print(log_file.read(), end='')

            # Check if the return value is a cubit object.
            if cubit_item_to_id(cubit_return) is not None:
                return CubitObject(self, cubit_return)
            elif isinstance(cubit_return, list):
                # If the return value is a list, check if any entry of the list
                # is a cubit object.
                return_list = []
                for item in cubit_return:
                    if cubit_item_to_id(item) is not None:
                        return_list.append(CubitObject(self, item))
                    elif is_base_type(item):
                        return_list.append(item)
                    else:
                        raise TypeError('Expected cubit object, or base_type, '
                            + 'got {}!'.format(item))
                return return_list
            elif is_base_type(cubit_return):
                return cubit_return
            else:
                raise TypeError('Expected cubit object, or base_type, '
                    + 'got {}!'.format(cubit_return))

            return cubit_return

        return function


class CubitObject(object):
    """
    This class holds a link to a cubit object in python2. Methods that are
    called on this class will 'really' be called in python2.
    """

    def __init__(self, cubit_connect, cubit_data_list):
        """
        Initialize the object.

        Args
        ----
        cubit_connect: CubitConnect
            A link to the cubit_connec object that will be used to call
            methods.
        cubit_data_list: []
            A list of strings that contains info about the cubit object.
            The first item is the id of this object in python2.
        """

        # Check formating of cubit_id.
        if cubit_item_to_id(cubit_data_list) is None:
            raise TypeError('Wrong type {}'.format(cubit_data_list))

        self.cubit_connect = cubit_connect
        self.cubit_id = cubit_data_list

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

    def __str__(self):
        """Return the string from python2."""
        return '<CubitObject>"' + self.cubit_id[1] + '"'
