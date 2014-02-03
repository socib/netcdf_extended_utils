__author__ = 'ksebastian'

import logging
import logging.config
from numpy import *
from es.socib.netcdf.modification_tools import NetcdfUpdater


def main():
    """
    /home/ksebastian/opendap/observational/drifter/surface_drifter/drifter_svp014-scb_svp009/L1/2013/dep0001_drifter-svp014_scb-svp009_L1_2013-12-02.nc
    """

    LOG_CONFIG_FILE = '../../../configuration/log.conf'
    logging.config.fileConfig(LOG_CONFIG_FILE, disable_existing_loggers=False)
    logger = logging.getLogger("netcdf_utils")

    netcdf_canonical_path = "/home/ksebastian/opendap/observational/drifter/surface_drifter/drifter_svp014-scb_svp009/L1/2013/dep0001_drifter-svp014_scb-svp009_L1_2013-12-02.nc"

    #
    # Initialize the variable data dictionary in the NetCDF file
    #
    new_variables_data = dict()
    trajectory_value = 'drifter-svp014_scb-svp009_L1'
    new_variables_data['trajectory'] = dict()
    new_variables_data['trajectory']['data'] = [None] * len(trajectory_value)
    # The string variables must be converted to an array
    for n in range(len(trajectory_value)):
        new_variables_data['trajectory']['data'][n] = trajectory_value[n]
        # Convert the array to a numpy array, for better functionality
    new_variables_data['trajectory']['data'] = array(new_variables_data['trajectory']['data'])
    new_variables_data['trajectory']['dimensions'] = ['name_strlen']

    #
    # Initialize the global attributes dictionary to be modified in the NetCDF file
    #
    new_global_attributes = dict()
    new_global_attributes['geospatial_lon_min'] = 0.76
    new_global_attributes['geospatial_lat_units'] = 'degrees_north_tmp'

    #
    # Initialize the variable attributes dictionary to be modified in the NetCDF file
    #
    new_variable_attributes = dict()
    new_variable_attributes['trajectory'] = {
        'new_attribute_string_name': 'new_attribute_string_value',
        'new_attribute_number_name': 5,
        'cf_role': 'cf-role attribute value modified'
    }

    # Create the parameters dictionary
    parameters = dict()
    parameters['netcdf_canonical_path'] = netcdf_canonical_path
    parameters['new_variables_data'] = new_variables_data
    parameters['new_global_attributes'] = new_global_attributes
    parameters['new_variable_attributes'] = new_variable_attributes

    # parameters = dict()

    NetcdfUpdater.modify_netcdf_file(**parameters)


if __name__ == "__main__":
    main()