# Cubitpy

A `python3` wrapper for Cubit. It is tested with Cubit13.2.

## Installation

It is recommended to use virtual environments with `python`.
On Debian systems the package `python3-venv` has to be installed.

```bash
sudo apt-get install python3-venv python3-dev
```

Now a virtual environment can be created (for example in the home directory)

```bash
cd ~
mkdir opt
cd opt
python3 -m venv cubitpy-env
```

The created virtual environment can be loaded with

```bash
source ~/opt/cubitpy-env/bin/activate
```

From now on we assume that the virtual enviroment is loaded.
To install `cubitpy` go to the repository directory

```bash
cd path_to_cubitpy
```

Run the following command to install the required packages

```bash
pip install -r requirements.txt
```

Add the cubitpy path to `PYTHONPATH`

```bash
export PYTHONPATH=path_to_cubitpy:$PYTHONPATH
```

Additionally paths to cubit and `pre_exodus` have to be set.

```bash
export BACI_PRE_EXODUS=path_to_pre-exodus
export CUBIT=path_to_cubit_directory
```

To check if everything worked as expected, run the tests

```bash
cd path_to_cubitpy/tests
python testing.py
```
