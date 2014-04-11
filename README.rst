NetCDF extended utils
=====================

Description
-----------

Extended netcdf utils to modify NetCDF files. Features:
  - Modify and add new variable values
  - Modify and add new global attributes
  - Modify and add new variable attributes
  - Delete global attributes, variables and dimensions

Limitations:
  - Only tested with NetCDF3 classic format
  - No support for groups.

Installation
------------

Install the requeriments::

  pip install numpy>=1.8.1 && pip install -r requirements.txt
  
**Note**: Install numpy first because of the `issue #4116 <https://github.com/numpy/numpy/issues/4116/>`_.

Install the NetCDF extended utils::
  
  python setup.py install
  
How to
------

The `tests <https://github.com/socib/netcdf_extended_utils/tree/master/tests>`_ folder has some examples to test some features.
  
  

