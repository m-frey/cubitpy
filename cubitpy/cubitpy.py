# -*- coding: utf-8 -*-
"""
Implements a class that helps create meshes with cubit. Since the cubit
interface works only with Python2, if Python3 is used, a wrapper for the cubit
methods is used.
"""


# Python modules.
import os
import shutil
import sys
import subprocess

# Cubitpy modules.
from . import cupy


def get_methods(cubit_object):
    """Return a list of all callable methods in object."""
    if (sys.version_info > (3, 0)):
        return cubit_object.cubit_connect.send_and_return(
            ['get_methods', cubit_object.cubit_id]
            )
    else:
        return [
            method_name for method_name in dir(cubit_object)
            if callable(getattr(cubit_object, method_name))
            ]


class CubitPy(object):
    """A wrapper class for cubit."""

    # Count the number of instances.
    _number_of_instances = 0

    def __init__(self, cubit_args=None, cubit_path=None, pre_exodus=None):
        """
        Initialize cubit.

        Args
        ----
        cubit_args: [str]
            List of arguments to pass to cubit.init.
        cubit_path: str
            Path to the cubit executables.
        cubit_log: str
            Path of the file where to write the cubit output to. The default
            value of /dev/null discards all output.
        pre_exodus: str
            Path to the pre_exodus pre-processor of baci.
        """

        # Get filepaths.
        if cubit_path is None:
            cubit_path = cupy.get_default_paths('cubit')
        if pre_exodus is None:
            pre_exodus = cupy.get_default_paths('pre_exodus')

        # Advance the instance counter.
        CubitPy._number_of_instances += 1

        # Arguments for cubit.
        if cubit_args is None:
            arguments = ['cubit',
                #'-log=/dev/null',    # Write the log to a file.
                '-information=Off',  # Do not output information of cubit.
                '-nojournal',        # Do write a journal file.
                '-noecho'            # Do not output commands used in cubit.
                ]
        else:
            arguments = ['cubit']
            for arg in cubit_args:
                arguments.appen(arg)

        # Depending on the python version, load the cubit default wrapper
        # (python2) or the modified wrapper for python3.
        if (sys.version_info > (3, 0)):
            # Python 3.
            from .cubit_wrapper3 import CubitConnect
            cubit_connect = CubitConnect(arguments)
            self.cubit = cubit_connect.cubit
        else:
            # Python 2.
            sys.path.append(cubit_path)
            import cubit  # @UnresolvedImport
            self.cubit = cubit
            # Initialize cubit.
            self.cubit.init(arguments)

        # Reset cubit.
        self.cubit.cmd('reset')
        self.cubit.cmd('set geometry engine acis')

        # Set lists and counters for blocks and sets.
        self._default_cubit_variables()

        # Content of head file.
        self.head = ''

        # Other parameters.
        self.cubit_path = cubit_path
        self.pre_exodus = pre_exodus

    def _default_cubit_variables(self):
        """
        Set the default values for the lists and counters used in cubit.
        """
        self.node_sets = []
        self.blocks = []
        self.node_set_counter = 1
        self.block_counter = 1

    def __del__(self):
        """
        When this object is deleted, remove the flag that an instance exitst.
        """
        CubitPy._number_of_instances -= 1

    def __getattr__(self, key, *args, **kwargs):
        """
        All calls to methods and attributes that are not in this object get
        passed to cubit. This function can only be used when there is a single
        instance of CubitPy.
        """

        # Check if more than one instance exits:
        if CubitPy._number_of_instances > 1:
            raise ValueError('There should be no other active instance of '
                + 'CubitPy! Check the CubitPy.reset() function to '
                + 'create multiple meshes with one script, or delete the'
                + 'existing CubitPy item (or let it run out of scope).')
        return self.cubit.__getattribute__(key, *args, **kwargs)

    def _get_type(self, item):
        """Return the type of item. It is expected to be a cubit geom item."""
        if (sys.version_info > (3, 0)):
            # Python 3.
            if self.cubit.cubit_connect.isinstance(item, cupy.vertex):
                return cupy.vertex
            elif self.cubit.cubit_connect.isinstance(item, cupy.curve):
                return cupy.curve
            elif self.cubit.cubit_connect.isinstance(item, cupy.surface):
                return cupy.surface
            elif self.cubit.cubit_connect.isinstance(item, cupy.volume):
                return cupy.volume
        else:
            if isinstance(item, self.cubit.Vertex):
                return cupy.vertex
            elif isinstance(item, self.cubit.Curve):
                return cupy.curve
            elif isinstance(item, self.cubit.Surface):
                return cupy.surface
            elif isinstance(item, self.cubit.Volume):
                return cupy.volume
        raise TypeError('Got {}!'.format(type(item)))

    def _get_type_string(self, item):
        """Return the string for the item in cubit commands."""
        item_type = self._get_type(item)
        if item_type == cupy.vertex:
            return 'vertex'
        elif item_type == cupy.curve:
            return 'curve'
        elif item_type == cupy.surface:
            return 'surface'
        elif item_type == cupy.volume:
            return 'volume'

    def add_element_type(self, item, el_type, name=None, bc=None):
        """
        Add a block to cubit that contains the geometry in item. Also set the
        element type of block.

        Args
        ----
        item: cubit.geom
            Geometry to set the element type for.
        el_type: str
            Cubit element type.
        name: str
            Name of the block.
        bc: [str]
            Data for the *.bc file that will be used with pre_exodus.
        """

        if self.block_counter == 0:
            self.cubit.cmd('reset block')

        self.cubit.cmd('block {} {} {}'.format(
            self.block_counter,
            self._get_type_string(item),
            item.id()
            ))
        self.cubit.cmd('block {} element type {}'.format(
            self.block_counter,
            el_type
            ))
        if name is not None:
            self.cubit.cmd('block {} name "{}"'.format(
                self.block_counter,
                name
                ))
        if bc is not None:
            self.blocks.append([self.block_counter, bc])
        self.block_counter += 1

    def add_node_set(self, item, name=None, bc=None):
        """
        Set the element type of item.

        Args
        ----
        item: cubit.geom
            Geometry to set the element type for.
        name: str
            Name of the node set.
        bc: [str]
            Data for the *.bc file that will be used with pre_exodus.
        """

        item_string = self._get_type_string(item)
        self.cubit.cmd('nodeset {} {} {}'.format(
            self.node_set_counter,
            item_string,
            item.id()
            ))
        if name is not None:
            self.cubit.cmd('nodeset {} name "{}"'.format(
                self.node_set_counter,
                name
                ))
        if bc is not None:
            self.node_sets.append([self.node_set_counter, bc])
        self.node_set_counter += 1

    def get_surface_center(self, surf):
        """
        Get a 3D point that has the local coordinated on the surface of (0,0)
        (parameter space ([-1,1],[-1,1])).
        """

        if not self._get_type(surf) == cupy.surface:
            raise TypeError('Did not expect {}'.format(type(surf)))

        range_u = surf.get_param_range_U()
        u = 0.5 * (range_u[1] + range_u[0])
        range_v = surf.get_param_range_V()
        v = 0.5 * (range_v[1] + range_v[0])
        return surf.position_from_u_v(u, v)

    def set_line_interval(self, item, n_el):
        """
        Set the number of elements along a line.

        Args
        ----
        item: cubit.curve
            The line that will be seeded into the intervals.
        n_el: int
            Number of intervals along line.
        """

        # Check if item is line.
        item_type = self._get_type(item)
        if not item_type == cupy.curve:
            raise TypeError('Expected line, got {}'.format(type(item)))
        self.cubit.cmd('curve {} interval {} scheme equal'.format(
            item.id(),
            n_el
            ))

    def export_cub(self, path):
        """Export the cubit input."""
        self.cubit.cmd('save as "{}" overwrite'.format(path))

    def export_exo(self, path):
        """Export the mesh."""
        self.cubit.cmd('export mesh "{}" overwrite'.format(path))

    def write_head_bc(self, head_path, bc_path):
        """Write the head and bc files that will be used with pre_exodus."""

        with open(head_path, 'w') as head_file:
            for line in self.head.split('\n'):
                head_file.write(line.strip())
                head_file.write('\n')

        with open(bc_path, 'w') as bc_file:
            bc_file.write('---------------------------------------BCSPECS\n\n')
            for block in self.blocks:
                bc_file.write((
                    '*eb{}="ELEMENT"\nsectionname="{}"\n'
                    + 'description="{}"\nelementname="{}"\n\n').format(
                        block[0], block[1][0], block[1][1], block[1][2]
                        ))
            for node_set in self.node_sets:
                bc_file.write((
                    '*ns{}="CONDITION"\nsectionname="{}"\n'
                    + 'description="{}"\n\n').format(
                        node_set[0], node_set[1][0], node_set[1][1]
                        ))

    def create_dat(self, dat_path):
        """
        This function creates a finished baci input *.dat file. First the mesh,
        head and bc files are written to a temp directory and then pre_exodus
        is called to create the *.dat file. The final input file is copied to
        dat_path.
        """

        # Check if output path exists.
        dat_dir = os.path.dirname(dat_path)
        if not os.path.exists(dat_dir):
            raise ValueError('Path {} does not exist!'.format(dat_dir))

        if not os.path.exists(cupy.temp_dir):
            os.makedirs(cupy.temp_dir)

        # Create files
        self.export_exo(os.path.join(cupy.temp_dir, 'cubitpy.exo'))
        self.write_head_bc(
            os.path.join(cupy.temp_dir, 'cubitpy.head'),
            os.path.join(cupy.temp_dir, 'cubitpy.bc')
            )

        # For debugging write the command to the temp folder.
        with open(os.path.join(cupy.temp_dir, 'cmd.sh'), 'w') as cmd_file:
            cmd_file.write(self.pre_exodus)
            cmd_file.write(' --exo=cubitpy.exo --bc=cubitpy.bc '
                + '--head=cubitpy.head')

        # Run pre_exodus.
        out = subprocess.check_output([
            self.pre_exodus,
            '--exo=cubitpy.exo',
            '--bc=cubitpy.bc',
            '--head=cubitpy.head'
            ], cwd=cupy.temp_dir)

        # Copy dat file.
        shutil.copyfile(
            os.path.join(cupy.temp_dir, 'cubitpy.dat'),
            dat_path
            )

    def reset(self):
        """
        Reset all objects in cubit and the created BCs and blocks and node
        sets.
        """

        self.cubit.reset()
        self._default_cubit_variables()

    def display_in_cubit(self, label=''):
        """
        Save the state to a cubit file and open cubit with that file.
        Additionally labels can be displayed in cubit to simplify the mesh
        creation process.

        Args
        ----
        label: []
            What kind of labels will be shown in cubit (vertex, curve, surf,
            vol).
        """

        if not os.path.exists(cupy.temp_dir):
            os.makedirs(cupy.temp_dir)
        state_path = os.path.join(cupy.temp_dir, 'state.cub')
        self.export_cub(state_path)

        # Write file that opens the state in cubit.
        journal_path = os.path.join(cupy.temp_dir, 'open_state.jou')
        with open(journal_path, 'w') as journal:
            journal.write('open "{}"\n'.format(state_path))

            # Label items in cubit.
            is_label = False
            if cupy.vertex in label:
                journal.write('label vertex On\n')
                is_label = True
            if cupy.curve in label:
                journal.write('label curve On\n')
                is_label = True
            if cupy.surface in label:
                journal.write('label surface On\n')
                is_label = True
            if cupy.volume in label:
                journal.write('label volume On\n')
                is_label = True

            if is_label:
                journal.write('display')

        # Open the state in cubit.
        subprocess.call([
            self.cubit_path,
            '-nojournal',
            '-information=Off',
            '-input', 'open_state.jou'
            ], cwd=cupy.temp_dir)
