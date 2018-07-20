


# Import python modules.
import execnet


import sys



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

    def init_cubit(self, arguments):

        # Initialize cubit.
        self.channel.send(['init', self.cubit_path, arguments])
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
        
        
        
        
                ## Send the call to cubit.
        #channel.send([self.cubit_id, key, [1,2,3]])
        #obj = channel.receive()
        #print(obj)
        
        
        #channel.send([obj, 'curves', []])
        #obj = channel.receive()
        #print(obj)
        
        
        
        
        return function


class CubitObject(object):
    def __init__(self, cubit_connect, cubit_id):
        
        if string_to_id(cubit_id) is None:
            raise TypeError('Wrong type {}'.format(cubit_id))
        
        self.cubit_connect = cubit_connect
        self.cubit_id = cubit_id

    
    def __getattribute__(self, key, *args, **kwargs):
        
        try:
            return object.__getattribute__(self, key, *args, **kwargs)
        except AttributeError:
            # pass to cubit connection
            return self.cubit_connect.get_function(self, key)
            


class Cubit(object):

    def init(self, args, cubit_path=None):

        # Get the cubit path from sys.path.
        if cubit_path is None:
            # Check if cubit is in one system path.
            for path in sys.path:
                if 'cubit' in path:
                    cubit_path = path

        # Set up the python2 interpreter.
        self.gw = execnet.makegateway("popen//python=python2.7")
        self.gw.reconfigure(py3str_as_py2str=True)

        # Load the python2 code.
        with open('/home/ivo/dev/cubitpy/cubitpy/cubit_wrapper2.py', 'r') as myfile:
            data = myfile.read()



    def get_cubit_function(self, key):
        
        
        def cubit_function(*args, **kwargs):
            print(args)
            print()
            self.channel.send([self.cubit_id, key, args])
            obj = self.channel.receive()
            return obj
        
        return cubit_function

    def __getattribute__(self, key, *args, **kwargs):
        print(key)
        object.__getattribute__(self, key)
        print(self.gw)
        return None

    def __getattr__(self, key, *args, **kwargs):
        """
        All calls to methods and attributes that are not in this object get
        passed to cubit.
        """
        
        ## Send the call to cubit.
        #channel.send([self.cubit_id, key, [1,2,3]])
        #obj = channel.receive()
        #print(obj)
        
        
        #channel.send([obj, 'curves', []])
        #obj = channel.receive()
        #print(obj)
        
        print(key)
        return self.get_cubit_function(key)
        print(args)
        #print(key)
        ##return self.cubit.__getattribute__(key, *args, **kwargs)


def print_arg(obj):

    list = (
        [method_name for method_name in dir(obj)
     if callable(getattr(obj, method_name))]
        )

    for item in list:
        print(item)




if False:

    gw = execnet.makegateway("popen//python=python2.7")
    gw.reconfigure(py3str_as_py2str=True)

    with open('/home/ivo/dev/cubitpy/cubitpy/cubit_wrapper2.py', 'r') as myfile:
        data = myfile.read()


    channel = gw.remote_exec(data)


    #print(channel.send(['init', '/opt/cubit-13.2/bin', ['cubit', '-noecho', '-nojournal','-log=aaa.txt']]))
    channel.send(['init', '/opt/cubit-13.2/bin', ['cubit', '-log=aaa.txt']])
    cubit_tt = channel.receive()

    for i in range(1):
        
        channel.send([cubit_tt, 'brick', [1,2,3]])
        obj = channel.receive()
        print(obj)
        
        
        channel.send([obj, 'curves', []])
        obj = channel.receive()
        print(obj)
        
        
        
        

    print(channel.send(None))




    print(channel.receive())





