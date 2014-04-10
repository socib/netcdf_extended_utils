__author__ = 'ksebastian'

import logging
import logging.config
from numpy import *
from netcdf_extended_utils.modification_tools import NetcdfUpdater
import os


def modify_netcdf_file_test():
    """
    Test the functionality of the modify_netcdf_file method
    """

    # Get the log.conf file absolute path
    LOG_CONFIG_FILE_REL_PATH = '../netcdf_extended_utils/configuration/log.conf'
    module_path = os.path.dirname(__file__)
    log_config_file_abs_path = os.path.join(module_path, LOG_CONFIG_FILE_REL_PATH)

    logging.config.fileConfig(log_config_file_abs_path, disable_existing_loggers=False)
    logger = logging.getLogger(__name__)

    netcdf_canonical_path = os.path.join(module_path, "dep0001_drifter-svp014_scb-svp009_L1_2013-12-02.nc")

    #
    # Initialize the variable data dictionary. Set the dictionary to modify the trajectory variable
    # value
    #
    new_variables_data = dict()
    trajectory_value = 'drifter-svp014_scb-svp009_L1_tmp'
    new_variables_data['trajectory'] = dict()
    new_variables_data['trajectory']['data'] = [None] * len(trajectory_value)
    # The string variables must be converted to an array
    for n in range(len(trajectory_value)):
        new_variables_data['trajectory']['data'][n] = trajectory_value[n]
    # Convert the array to a numpy array, for better functionality
    new_variables_data['trajectory']['data'] = array(new_variables_data['trajectory']['data'])
    new_variables_data['trajectory']['dimensions'] = ['name_strlen']

    #
    # Initialize the global attributes dictionary. Set the dictionary to modify the
    # the some global attributes values
    #
    new_global_attributes = dict()
    new_global_attributes['geospatial_lon_min'] = 0.76
    new_global_attributes['geospatial_lat_units'] = 'degrees_north_tmp'

    #
    # Initialize the variable attributes dictionary. Set the dictionary to modify some
    # attributes of the variable trajectory
    #
    new_variable_attributes = dict()
    new_variable_attributes['trajectory'] = {
        'new_attribute_string_name': 'new_attribute_string_value',
        'new_attribute_number_name': 5,
        'cf_role': 'cf-role attribute value modified'
    }

    # Initialize the remove elements dictionary. Set the dictionary to remove the cdm_data_type global attribute and
    # the LOCCLASS variable
    remove_elements = dict();
    remove_elements['remove_global_attributes'] = set(['cdm_data_type'])
    remove_elements['remove_variables'] = set(['LOCCLASS'])

    # Create the parameters dictionary
    parameters = dict()
    parameters['netcdf_canonical_path'] = netcdf_canonical_path
    parameters['new_variables_data'] = new_variables_data
    parameters['new_global_attributes'] = new_global_attributes
    parameters['new_variable_attributes'] = new_variable_attributes
    parameters['remove_elements'] = remove_elements

    NetcdfUpdater.modify_netcdf_file(**parameters)

    assert True