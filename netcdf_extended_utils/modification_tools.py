import logging
from netCDF4 import Dataset
from numpy import *
import os

__author__ = 'ksebastian'

logger = logging.getLogger(__name__)


class NetcdfUpdater:

    """
    Class with the method modify_netcdf_file. This method allows to modify global attributes, variables and variable
    attributes from a NetCDF file.
    """

    __REMOVE_GLOBAL_ATTRIBUTES_KEY = 'remove_global_attributes'
    __REMOVE_VARIABLES_KEY = 'remove_variables'
    __REMOVE_DIMENSIONS = 'remove_dimensions'

    def __init__(self):
        """

        :return:

        """

    @staticmethod
    def modify_netcdf_file(netcdf_canonical_path=None, new_variables_data=dict(), new_global_attributes=dict(),
                           new_variable_attributes=dict(),
                           remove_elements=dict({
                               'remove_global_attributes': set(),
                               'remove_variables': set(),
                               'remove_dimensions': set(),

                           }),
                           keep_tmp_file=True):
        """
        Modify the NetCDF file. Features:
            - Modify and add new variable values
            - Modify and add new global attributes
            - Modify and add new variable attributes
            - Delete global attributes, variables and dimensions

        Limitations:
            - Only tested with NetCDF3 classic format
            - Not support groups.

        Creates new variables, attributes, dimensions or global attributes when them not exist in the NetCDF file.
        Otherwise update the them. This method, by default, keep the original file without change it, creating another
        file with the same name as the original with the suffix "_tmp".

        :type netcdf_canonical_path: str
        :param netcdf_canonical_path: the canonical path to the NetCDF file

        :type new_global_attributes: dict
        :param new_global_attributes: the new global attributes to be updated/added in the NetCDF file.
            Format::

                {
                    # The value must str or number
                    "global_attribute": value,
                    ...
                }

        :type new_variable_attributes: dict
        :param new_variable_attributes: The new variable attributes to be updated/added in the NetCDF file.
            Format::

                {
                    "variable_name_1": {
                        # The value must str or number
                        "variable_attribute_name": value,
                         ...
                    }
                    ...
                }

        :type new_variables_data: dict
        :param new_variables_data: The new variable data to be updated in the NetCDF file.
            Format::

                {
                    "variable_name_1": {
                        # Numpy Array from 1 to N dimensions
                        "data": array()
                        # The dimensions of the variable with the same order of the shape data
                        "dimensions": ["dimension_name_1", "dimension_name_2"]
                        # The data type from DType class
                        "type": str()
                    },
                    ...
                }

        :type keep_tmp_file bool:
        :param keep_tmp_file:
            If true keep the temporally file with the changes. The name is the same as the original
            file with the prefix "_tmp". Otherwise the original file is deleted and the temporally file is renamed as the
            original file.

        :type remove_elements: dict
        :param remove_elements:
            Format::

                {
                    "remove_global_attributes": Set()
                    "remove_variables": Set()
                    "remove_dimensions": Set()
                }

        """

        if netcdf_canonical_path is None:
            warnings.warn('NetCDF canonical path is None')
            return

        # Check that the remove elements dictionary has the desirable keys
        if not NetcdfUpdater.__REMOVE_GLOBAL_ATTRIBUTES_KEY in remove_elements:
            remove_elements[NetcdfUpdater.__REMOVE_GLOBAL_ATTRIBUTES_KEY] = set()
        if not NetcdfUpdater.__REMOVE_VARIABLES_KEY in remove_elements:
            remove_elements[NetcdfUpdater.__REMOVE_VARIABLES_KEY] = set()
        if not NetcdfUpdater.__REMOVE_DIMENSIONS in remove_elements:
            remove_elements[NetcdfUpdater.__REMOVE_DIMENSIONS] = set()

        logger.debug('Modifying NetCDF file ' + netcdf_canonical_path)

        # Calculate the new dimension lengths from the new variable data
        new_dimensions_len = NetcdfUpdater.__get_new_dimensions_len(new_variables_data)

        # Open the NetCDF file in read mode to retrieve the needed information that is going
        # to be inserted in the temporally NetCDF file
        org_file = Dataset(netcdf_canonical_path, 'r')

        # Create a temporally NetCDF file which is going to be modified.
        new_file = Dataset(netcdf_canonical_path + '_tmp', 'w', format=org_file.file_format)

        # Set the new NetCDF global attributes from the given NetCDF file and the given new global attributes if
        # them exists. IMPORTANT: The below method doesn't preserve the original dictionary order
        #### new_file.setncatts(dict(org_file.__dict__, **new_global_attributes))
        # new_file.setncatts(org_file.__dict__)
        for key, value in org_file.__dict__.iteritems():

            # Do not add global attributes to delete
            if key in remove_elements['remove_global_attributes']:
                continue

            new_file.setncattr(key, value)

        for key, value in new_global_attributes.items():
            new_file.setncattr(key, value)

        # Update the NetCDF dimensions from the original NetCDF file
        for dimension_name in org_file.dimensions.keys():

            # Do not add dimensions to delete
            if dimension_name in remove_elements['remove_dimensions']:
                continue

            dimension = org_file.dimensions[dimension_name]

            # Set the time dimension as unlimited dimension only if is time dimension
            if dimension_name == 'time':
                new_file.createDimension(dimension_name, 0)
            # If the dimension length has changed, get the new length and se it
            elif dimension_name in new_dimensions_len:
                new_file.createDimension(dimension_name, new_dimensions_len[dimension_name])
            # Otherwise set the original dimension length
            else:
                new_file.createDimension(dimension_name, len(dimension))

        # Create the dimensions that there are not in the original NetCDF file
        for dimension_name, dimension_len in new_dimensions_len.iteritems():

            # Only creates the dimension if it is no in the original NetCDF file
            if dimension_name in org_file.dimensions:
                continue

            new_file.createDimension(dimension_name, dimension_len)

        # Update the NetCDF variables from the original NetCDF file
        for v_name in org_file.variables.keys():

            # Do not add variables to delete
            if v_name in remove_elements['remove_variables']:
                continue

            v = org_file.variables[v_name]
            # The dtype attribute allways has the | character at the first position.
            # It must be deleted to create the variable in the new NetCDF file
            d_type = str(v.dtype).replace("|", "")

            # Check if the variable values has to be modified. The new values must
            # be in the variable_values dict. If has the type attribute then the variable is created with the given
            # type and dimensions. Otherwise it is created with the original type and dimensions
            if v_name in new_variables_data:
                if 'type' in new_variables_data[v_name]:
                    new_variable = new_file.createVariable(v_name,
                                                           new_variables_data[v_name]['type'],
                                                           new_variables_data[v_name]['dimensions'])
                else:
                    new_variable = new_file.createVariable(v_name, d_type, v.dimensions)
                new_variable[:] = new_variables_data[v_name]['data'][:]
            else:
                new_variable = new_file.createVariable(v_name, d_type, v.dimensions)
                new_variable[:] = v[:]

            # Set the variable attributes from the original attributes and the given new variable attributes if
            # them exist
            new_variable.setncatts(v.__dict__)
            if v_name in new_variable_attributes:
                for key, value in new_variable_attributes[v_name].items():
                    new_variable.setncattr(key, value)

        # Create the NetCDF variables from the original NetCDF file
        for v_name, value in new_variables_data.iteritems():

            # Only creates the variable if it isn't in the original NetCDF file
            if v_name in org_file.variables:
                continue

            # Create the variable in the new file and set the variable attributes
            new_variable = new_file.createVariable(v_name, value['type'], value['dimensions'])
            new_variable.setncatts(new_variable_attributes[v_name])
            new_variable[:] = value['data']

        new_file.close()
        org_file.close()

        # Remove the original NetCDF file and rename the temporally file with the original name
        if not keep_tmp_file:
            os.remove(netcdf_canonical_path)
            os.rename(netcdf_canonical_path + '_tmp', netcdf_canonical_path)

        logger.debug('NetCDF file updated --> ' + netcdf_canonical_path)

    @staticmethod
    def __get_new_dimensions_len(new_variable_data):
        """
        Return the new lengths of the dimensions, calculated from the given variable data.

        :type new_variables_data: dict()
            Format::
                {
                    "variable_name_1": {
                        # Numpy Array from 1 to N dimensions
                        "data": array()
                        # The dimensions of the variable ordered as the data shape
                        "dimensions": ["dimension_name_1", "dimension_name_2"]
                    },
                    ...
                }

        :param new_variables_data: The new variable data to be updated/added in the NetCDF file.

        :rtype: dict()
            Format::
            {
                 # Dimension length
                "dimension_name": int(),
                ...
            }
        :return: the new lengths of the dimensions

        """

        # The new dimensions lengths dictionary
        new_dimensions_len = dict()

        for variable_name in new_variable_data:

            variable_data = new_variable_data[variable_name]

            # Check the existence of the dimensions key
            try:
                dimensions = variable_data['dimensions']
            except KeyError, e:
                msg = " Each key (variable name) value must have the dimensions key. This represents the dimensions of" \
                      " the variable ordered as the data shape. The input value is " + str(variable_data)
                e.args += (msg,)
                raise

            for dimension_idx in range(len(dimensions)):

                dimension_name = variable_data['dimensions'][dimension_idx]

                # Check the existence of the data key
                try:
                    data = variable_data['data']
                except KeyError, e:
                    msg = " Each key (variable name) value must have the data key. The value of this key must be a " \
                          "numpy Array from 1 to N dimensions.  The input value is: " + str(variable_data)
                    e.args += (msg,)
                    raise

                # Check that the data key is a numpy array
                try:
                    dimension_len = data.shape[dimension_idx]
                except AttributeError, e:
                    msg = " The value of the variable data must be a numpy array. The type of the data is " + \
                          str(type(data))
                    e.args += (msg,)
                    raise

                new_dimensions_len[dimension_name] = dimension_len

        return new_dimensions_len