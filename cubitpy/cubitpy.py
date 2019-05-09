# -*- coding: utf-8 -*-
"""
Implements a class that helps create meshes with cubit. Since the cubit
interface works only with Python2, a wrapper for the cubit methods is used.
"""


# Python modules.
import os
import shutil
import subprocess

# Cubitpy modules.
from .conf import cupy
from .cubit_group import CubitGroup
from .utility_functions import check_environment_eclipse


class CubitPy(object):
    """A wrapper class for cubit."""

    def __init__(self, *, cubit_args=None, cubit_path=None, pre_exodus=None):
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
            pre_exodus = cupy.get_default_paths('pre_exodus', False)

        # Arguments for cubit.
        if cubit_args is None:
            arguments = ['cubit',
#                '-log=/dev/null',    # Write the log to a file.
                '-information=Off',  # Do not output information of cubit.
                '-nojournal',        # Do write a journal file.
                '-noecho'            # Do not output commands used in cubit.
                ]
        else:
            arguments = ['cubit']
            for arg in cubit_args:
                arguments.append(arg)

        # Load the cubit wrapper.
        from .cubit_wrapper3 import CubitConnect
        cubit_connect = CubitConnect(arguments,
            cubit_bin_path=os.path.join(cubit_path, 'bin'))
        self.cubit = cubit_connect.cubit

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

    def __getattr__(self, key, *args, **kwargs):
        """
        All calls to methods and attributes that are not in this object get
        passed to cubit.
        """
        return self.cubit.__getattribute__(key, *args, **kwargs)

    def add_element_type(self, item, el_type, name=None, bc=None):
        """
        Add a block to cubit that contains the geometry in item. Also set the
        element type of block.

        Args
        ----
        item: CubitObject
            Geometry to set the element type for.
        el_type: str
            Cubit element type.
        name: str
            Name of the block.
        bc: [str]
            Data for the *.bc file that will be used with pre_exodus.
        """

        if self.block_counter == 1:
            self.cubit.cmd('reset block')

        # Get element type of item.
        geometry_type = item.get_geometry_type()

        # For now only 3D elements are allowed.
        if geometry_type is not cupy.geometry.volume:
            raise TypeError('For now element types can only be set for '
                + 'volumes!')

        # Execute the block commands in cubit.
        self.cubit.cmd('block {} {} {}'.format(
            self.block_counter,
            geometry_type.get_cubit_string(),
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
        Add a node set to cubit. This node set can have a boundary condition.

        Args
        ----
        item: CubitObject
            Geometry whose nodes will be put into the node set.
        name: str
            Name of the node set.
        bc: [str1 / BoundaryConditionType, str2]
            Data for the *.bc file that will be used with pre_exodus.
            - str1: Header for the .dat file section. Can also be given as
                BoundaryConditionType, where the header is automatically
                generated.
            - str2: Line with the concret definition of the boundary condition.
        """

        # Get element type of item.
        geometry_type = item.get_geometry_type()

        # Add the node set to cubit.
        self.cubit.cmd('nodeset {} {} {}'.format(
            self.node_set_counter,
            geometry_type.get_cubit_string(),
            item.id()
            ))
        if name is not None:
            self.cubit.cmd('nodeset {} name "{}"'.format(
                self.node_set_counter,
                name
                ))
        if bc is not None:
            # Check if the name of the boundary condition is given explicitly.
            if isinstance(bc[0], cupy.bc_type):
                bc_string = bc[0].get_dat_bc_section_header(geometry_type)
            else:
                bc_string = bc[0]
            self.node_sets.append([self.node_set_counter, [bc_string, bc[1]]])
        self.node_set_counter += 1

    def get_surface_center(self, surf):
        """
        Get a 3D point that has the local coordinated on the surface of (0,0)
        (parameter space ([-1,1],[-1,1])).
        """

        if not surf.get_geometry_type() == cupy.geometry.surface:
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
        if not item.get_geometry_type() == cupy.geometry.curve:
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
        Create the dat file an copy it to dat_path.
        """

        # Check if output path exists.
        dat_dir = os.path.dirname(dat_path)
        if not os.path.exists(dat_dir):
            raise ValueError('Path {} does not exist!'.format(dat_dir))

        # Create the dat file.
        temp_dat_file = self._create_dat()

        # Copy dat file.
        shutil.copyfile(temp_dat_file, dat_path)

    def _create_dat(self):
        """
        This function creates a finished baci input *.dat file. First the mesh,
        head and bc files are written to a temp directory and then pre_exodus
        is called to create the *.dat file.
        """

        # Check if the path to pre_exodus is valid.
        if self.pre_exodus is None:
            raise ValueError('The path to pre_exodus is None!')

        os.makedirs(cupy.temp_dir, exist_ok=True)

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
        _out = subprocess.check_output([
            self.pre_exodus,
            '--exo=cubitpy.exo',
            '--bc=cubitpy.bc',
            '--head=cubitpy.head'
            ], cwd=cupy.temp_dir)

        # Return the path to the dat file.
        return os.path.join(cupy.temp_dir, 'cubitpy.dat')

    def group(self, name, add_value=None):
        """
        Reference a group in cubit. Depending on the passed keyword arguments
        the group is created or just references an existing group.
        """
        return CubitGroup(self, name, add_value)

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

        os.makedirs(cupy.temp_dir, exist_ok=True)
        state_path = os.path.join(cupy.temp_dir, 'state.cub')
        self.export_cub(state_path)

        # Write file that opens the state in cubit.
        journal_path = os.path.join(cupy.temp_dir, 'open_state.jou')
        with open(journal_path, 'w') as journal:
            journal.write('open "{}"\n'.format(state_path))

            # Label items in cubit.
            for item in label:
                journal.write('label {} On\n'.format(item.get_cubit_string()))

            if len(label) > 0:
                journal.write('display')

        # Adapt the environment if needed.
        is_eclipse, python_path_old = check_environment_eclipse()

        # Open the state in cubit.
        subprocess.call([
            os.path.join(self.cubit_path, 'cubit'),
            '-nojournal',
            '-information=Off',
            '-input', 'open_state.jou'
            ], cwd=cupy.temp_dir)

        # Restore environment path.
        if is_eclipse:
            os.environ['PYTHONPATH'] = python_path_old
