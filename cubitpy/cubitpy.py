# -*- coding: utf-8 -*-

# Python modules.
import os
import shutil
import sys
import subprocess


class CubitOptions(object):
    """Object for types in cubitpy."""
    def __init__(self):

        # Element types
        self.vertex = 'cubitpy_vertex'
        self.curve = 'cubitpy_curve'
        self.surface = 'cubitpy_surface'
        self.volume = 'cubitpy_volume'


# Global object with options for cubitpy.
cupy = CubitOptions()


class CubitPy(object):
    """A wrapper class for cubit."""

    def __init__(self, cubit_args=None, cubit_path='/opt/cubit-13.2/bin',
            pre_exodus='/home/ivo/baci/work/release/pre_exodus'):
        """
        Initialize cubit.

        Args
        ----
        cubit_args: [str]
            List of arguments to pass to cubit.init.
        cubit_path: str
            Path to the cubit executables.
        """

        # Load cubit.
        sys.path.append(cubit_path)
        import cubit  # @UnresolvedImport
        self.cubit = cubit

        # Initialize cubit.
        if cubit_args is None:
            self.cubit.init(['cubit', '-noecho', '-nojournal'])
        else:
            arguments = ['cubit']
            for arg in cubit_args:
                arguments.appen(arg)
            self.cubit.init(arguments)

        # Reset cubit.
        self.cubit.cmd('reset')
        self.cubit.cmd('set geometry engine acis')

        # Set lists and counters for blocks and sets.
        self.node_sets = []
        self.blocks = []
        self.node_set_counter = 1
        self.block_counter = 1

        # Content of head file.
        self.head = ''

        # Other parameters.
        self.pre_exodus = pre_exodus

    def __getattr__(self, key, *args, **kwargs):
        """
        All calls to methods and attributes that are not in this object get
        passed to cubit.
        """
        return self.cubit.__getattribute__(key, *args, **kwargs)

    def _get_type(self, item):
        """Return the type of item. It is expected to be a cubit geom item."""
        if isinstance(item, self.cubit.Vertex):
            return cupy.vertex
        elif isinstance(item, self.cubit.Curve):
            return cupy.curve
        elif isinstance(item, self.cubit.Surface):
            return cupy.surface
        elif isinstance(item, self.cubit.Volume):
            return cupy.volume
        else:
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
            self.cubit.cmp('reset block')
        print('block {} {} {}'.format(
            self.block_counter,
            self._get_type_string(item),
            item.id()
            ))
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
            bc_file.write('----------------------------------------BCSPECS\n\n')
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
        head and bc files are written to a temp directory and then pre_exodus is
        called to create the *.dat file. The final input file is copied to
        dat_path.
        """

        temp_dir = '/tmp/cubitpy'
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        # Create files
        self.export_exo(os.path.join(temp_dir, 'cubitpy.exo'))
        self.write_head_bc(
            os.path.join(temp_dir, 'cubitpy.head'),
            os.path.join(temp_dir, 'cubitpy.bc')
            )

        # For debugging write the command to the temp folder.
        with open(os.path.join(temp_dir, 'cmd.sh'), 'w') as cmd_file:
            cmd_file.write(self.pre_exodus)
            cmd_file.write(' --exo=cubitpy.exo --bc=cubitpy.bc --head=cubitpy.head')

        # Run pre_exodus.
        out = subprocess.check_output([
            self.pre_exodus,
            '--exo=cubitpy.exo',
            '--bc=cubitpy.bc',
            '--head=cubitpy.head'
            ], cwd=temp_dir)

        # Check if path exists.
        dat_dir = os.path.abspath(os.path.join(dat_path, os.pardir))
        if not os.path.exists(dat_dir):
            raise ValueError('Path {} does not exist!'.format(dat_dir))

        # Copy dat file.
        shutil.copyfile(
            os.path.join(temp_dir, 'cubitpy.dat'),
            dat_path
            )

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

        temp_path = '/tmp/cubitpy'
        if not os.path.exists(temp_path):
            os.makedirs(temp_path)
        state_path = os.path.join(temp_path, 'state.cub')
        self.export_cub(state_path)

        # Write file that opens the state in cubit.
        journal_path = os.path.join(temp_path, 'open_state.jou')
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
            '/opt/cubit-13.2/cubit',
            '-nojournal',
            '-input', 'open_state.jou'
            ], cwd=temp_path)
