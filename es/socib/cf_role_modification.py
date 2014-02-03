from django.db.models.query import QuerySet

__author__ = 'ksebastian'

import logging
import logging.config
from numpy import *
import os
import re
from es.socib.netcdf.modification_tools import NetcdfUpdater
from es.socib.netcdf.attribute_names_values import *
from es.socib.netcdf.d_type import *
from es.socib.utils.regexp_utils import RegexpUtils
from model_data_base.models import *


LOG_CONFIG_FILE = '../../configuration/log.conf'
logging.config.fileConfig(LOG_CONFIG_FILE, disable_existing_loggers=False)
logger = logging.getLogger("netcdf_utils")


def main():
    """
    This application walks inside a base directory to find the NetCDF files. For each file modify/add the cf role
    variable and feature type global attributes.

    """

    #base_dir = '/data/current/opendap/observational'
    base_dir = '/home/ksebastian/opendap/observational/drifter/'

    logger.info("**********************************")
    logger.info("* Modifying the cf role variable *")
    logger.info("**********************************")

    # Build the regexp with excluded files and directories
    reg_exp = RegexpUtils.build_reg_exp()

    for root, subFolders, file_names in os.walk(base_dir):

        subFolders[:] = [os.path.join(root, d) for d in subFolders]
        subFolders[:] = [d for d in subFolders if not re.search(reg_exp, d)]

        for file_name in file_names:

            f = os.path.join(root, file_name)
            if re.search(reg_exp, f):
                continue

            logger.info('Updating NetCDF file ' + f)

            # Initialize the variable data, variable attributes and global attributes dictionaries
            new_variables_data = dict()
            new_variable_attributes = dict()
            new_global_attributes = dict()

            # Generates the dictionary values with the
            add_cf_role_variable_and_global_attributes(file_name, new_variables_data, new_variable_attributes,
                                                       new_global_attributes)

            logger.debug('cf_role variable: ' + str(new_variables_data))
            logger.debug('cf_role variable attributes: ' + str(new_variable_attributes))

            # Create the parameters dictionary
            parameters = dict()
            parameters['netcdf_canonical_path'] = f
            parameters['new_variables_data'] = new_variables_data
            parameters['new_variable_attributes'] = new_variable_attributes
            parameters['new_global_attributes'] = new_global_attributes

            NetcdfUpdater.modify_netcdf_file(**parameters)

            logger.info('Updated NetCDF file ' + f)


def add_cf_role_variable_and_global_attributes(netcdf_canonical_path, new_variables_data, new_variable_attributes,
                                               new_global_attributes):
    """
    Add the cf role variable value, dimensions, type, attributes and global attributes to the dictionaries, following
    the specification of the es.socib.netcdf.modfication_tools.NetcdfUpdater.modify_netcdf_file() method.

    The platform name and instrument name is extracted from the netcdf canonical path to perform the search of the
    process platform. If is a platform product then the instrument of the process platform is set to None. From
    the process platform is extracted the feature type to add the information to the dictionaries.

    TRICKS:

    The glider L2 products must be trajectory profile and the processing application doesn't have the needed
    information to know that is a trajectory profile data. It is necessary check the file name to identify the
    the glider L2 products and change the feature type value

    Only the latest awac instrument is configured to be processed. So to find the process platform the instrument name
    of awac instruments is set to 'scb-awac' (the digits are removed)

    :type netcdf_canonical_path: str
    :param netcdf_canonical_path: Specified at the es.socib.netcdf.modfication_tools.NetcdfUpdater.modify_netcdf_file()
    method

    :type new_variables_data: dict()
    :param new_variables_data: Specified at the es.socib.netcdf.modfication_tools.NetcdfUpdater.modify_netcdf_file()
    method

    :type new_variable_attributes: dict()
    :param new_variable_attributes: Specified at the es.socib.netcdf.modfication_tools.NetcdfUpdater.modify_netcdf_file()
    method

    :type new_global_attributes: dict()
    :param new_global_attributes: Specified at the es.socib.netcdf.modfication_tools.NetcdfUpdater.modify_netcdf_file()
    method
    """

    trajectory_value = ''
    file_name_split = netcdf_canonical_path.split('_')

    platform_name = file_name_split[1]
    instrument_name = None
    is_platform_product = False

    # Identify if the NetCDF is a platform product
    if len(file_name_split) == 4:
        is_platform_product = True

    # Get the platform product and cf role string value
    if is_platform_product:

        processing_level = file_name_split[2]

        try:
            process_platform = ProcessPlatform.objects.get(
                process_platform_instrument=None,
                process_platform_platform__platform_name__icontains=platform_name.replace('-', '_'))
        except Exception, e:
            msg = " Searching for process platform with the paltform name " + platform_name + " and instrument name " +\
                instrument_name
            e.args += (msg,)
            raise

        feature_type = process_platform.process_platform_cf_feature_type

        if process_platform.process_platform_instrument_type is None:
            type_name = process_platform.process_platform_platform.platform_instrument_type.get_convention_file_name()
        else:
            type_name = process_platform.process_platform_instrument_type.get_convention_file_name()

        cf_role_string_value = platform_name + '_' + type_name + '_' + processing_level

    else:

        instrument_name = file_name_split[2]
        modified_instrument = instrument_name
        processing_level = file_name_split[3]

        # Trick!
        # Only the latest awac instrument is configured to be processed.
        if instrument_name.find('scb-awac') != -1:
            modified_instrument = 'scb-awac'

        try:
            process_platform = ProcessPlatform.objects.get(
                process_platform_instrument__instrument_name__icontains=modified_instrument,
                process_platform_platform__platform_name__icontains=platform_name.replace('-', '_'))
        except Exception, e:
            msg = " Searching for process platform with platform name " + platform_name + " and instrument name " +\
                instrument_name
            e.args += (msg,)
            raise

        feature_type = process_platform.process_platform_cf_feature_type
        cf_role_string_value = platform_name + '_' + instrument_name + '_' + processing_level

    parameters = dict()
    parameters['new_variables_data'] = new_variables_data

    # Trick!
    # The glider L2 products must be trajectory profile and the processing application doesn't have the needed
    # information to know that is a trajectory profile data. It is necessary check the file name to identify the
    # the glider L2 products
    feature_type = modify_feature_type_value(feature_type, netcdf_canonical_path)

    # char station_name(name_strlen) ;
    #    station_name:long_name = "station name" ;
    #    station_name:cf_role = "timeseries_id";
    if feature_type == FeatureTypeValue.time_series:

        new_global_attributes[AttributeName.cdm_data_type] = FeatureTypeValue.time_series
        new_global_attributes[AttributeName.cf_feature_type] = FeatureTypeValue.time_series
        new_global_attributes[AttributeName.feature_type] = FeatureTypeValue.time_series

        parameters['cf_role_variable_name'] = VariableName.station_name
        parameters['dimensions'] = [DimensionName.name_strlen]
        new_variable_attributes[VariableName.station_name] = {
            AttributeName.long_name: 'station name',
            AttributeName.cf_role: CFRoleValue.time_series_id,
        }
        parameters['cf_role_value'] = cf_role_string_value

    # char station_name(name_strlen) ;
    #     station_name:long_name = "station name" ;
    #     station_name:cf_role = "timeseries_id" ;
    elif feature_type == FeatureTypeValue.time_series_profile:

        new_global_attributes[AttributeName.cdm_data_type] = FeatureTypeValue.time_series_profile
        new_global_attributes[AttributeName.cf_feature_type] = FeatureTypeValue.time_series_profile
        new_global_attributes[AttributeName.feature_type] = FeatureTypeValue.time_series_profile

        parameters['cf_role_variable_name'] = VariableName.station_name
        parameters['dimensions'] = [DimensionName.name_strlen]
        new_variable_attributes[VariableName.station_name] = {
            AttributeName.long_name: 'station name',
            AttributeName.cf_role: CFRoleValue.time_series_id
        }
        parameters['cf_role_value'] = cf_role_string_value

    # char trajectory(name_strlen) ;
    #   trajectory:cf_role = "trajectory_id";
    elif feature_type == FeatureTypeValue.trajectory:

        new_global_attributes[AttributeName.cdm_data_type] = FeatureTypeValue.trajectory
        new_global_attributes[AttributeName.cf_feature_type] = FeatureTypeValue.trajectory
        new_global_attributes[AttributeName.feature_type] = FeatureTypeValue.trajectory

        parameters['cf_role_variable_name'] = VariableName.trajectory
        parameters['dimensions'] = [DimensionName.name_strlen]
        new_variable_attributes[VariableName.trajectory] = {
            AttributeName.cf_role: CFRoleValue.trajectory_id
        }
        parameters['cf_role_value'] = cf_role_string_value

    # int trajectory;
    #     trajectory:cf_role = "trajectory_id" ;
    # NOTE: The trajectory variable for trajectory profile also could be string value
    elif feature_type == FeatureTypeValue.trajectory_profile:

        new_global_attributes[AttributeName.cdm_data_type] = FeatureTypeValue.trajectory_profile
        new_global_attributes[AttributeName.cf_feature_type] = FeatureTypeValue.trajectory_profile
        new_global_attributes[AttributeName.feature_type] = FeatureTypeValue.trajectory_profile

        parameters['cf_role_variable_name'] = VariableName.trajectory
        parameters['dimensions'] = [DimensionName.name_strlen]
        new_variable_attributes[VariableName.trajectory] = {
            AttributeName.cf_role: CFRoleValue.trajectory_id
        }
        parameters['cf_role_value'] = cf_role_string_value

        add_cf_role_variable(**parameters)
    else:
        raise TypeError('The feature type must be one the following: ' +
                        FeatureTypeValue.get_available_feature_type_values())

    # The cdm_data_type value must have the first letter upper case (ERDAP compatibility)
    new_global_attributes[AttributeName.cdm_data_type] = upper_case_first_character(
        new_global_attributes[AttributeName.cdm_data_type])

    # Add the cf_role variable to the new variables data dictionary
    add_cf_role_variable(**parameters)


def add_cf_role_variable(cf_role_variable_name, dimensions, cf_role_value,
                         new_variables_data):

    """
    Add the given cf role variable with the given dimensions and value the given dictionary. Only str, unicode or int
    values are allowed

    :type cf_role_variable_name: str
    :param cf_role_variable_name: the cf role variable name

    :type dimensions: array
    :param dimensions: The cf role variable dimensions

    :type cf_role_value: str, unicode or int
    :param cf_role_value: the cf role value

    :type new_variables_data: dict()
    :param new_variables_data: Specified at the es.socib.netcdf.modfication_tools.NetcdfUpdater.modify_netcdf_file()
    method

    :raise: TypeError()
    """
    new_variables_data[cf_role_variable_name] = dict()
    new_variables_data[cf_role_variable_name]['dimensions'] = dimensions

    # I do not know well why the cf role value is unicode??
    if isinstance(cf_role_value, unicode) or isinstance(cf_role_value, str):

        new_variables_data[cf_role_variable_name]['data'] = [None] * len(cf_role_value)
        # The string variables must be converted to an array
        for n in range(len(cf_role_value)):
            new_variables_data[cf_role_variable_name]['data'][n] = cf_role_value[n]
        # Convert the array to a numpy array, for better functionality
        new_variables_data[cf_role_variable_name]['data'] = array(new_variables_data[cf_role_variable_name]['data'])
        new_variables_data[cf_role_variable_name]['type'] = DType.single_character

    elif isinstance(cf_role_value, int):

        new_variables_data[cf_role_variable_name]['data'] = cf_role_value
        new_variables_data[cf_role_variable_name]['type'] = DType.nc_int

    else:
        raise TypeError('The cf role value must be int, unicode or str')


def modify_feature_type_value(feature_type, file_name):

    """
    Modify the feature type for glider L2 product. To identify it is used the file name and the regexp
    '.*([s|i]deep|icoast).*_L2_.*_data_dt.nc'

    The glider L2 products must be trajectory profile and the processing application doesn't have the needed
    information to know that is a trajectory profile data. It is necessary check the file name to identify the
    the glider L2 products and change the feature type value


    :type feature_type: str
    :param feature_type: the original feature type

    :type file_name: str
    :param file_name: the NetCDF file name

    :return: The original feature type if is not a glider L2 product, Otherwise return
    FeatureTypeValue.trajectory_profile

    """

    #
    reg_exp = '.*([s|i]deep|icoast).*_L2_.*_data_dt.nc'
    if not re.search(reg_exp, file_name):
        return feature_type

    return FeatureTypeValue.trajectory_profile


def upper_case_first_character(s):

    """
    Upper case the first character of the given string

    :type s: str
    :param s: The string to be upper case the first character

    :return: The string with the first character upper case
    """
    return s[0].upper() + s[1:]


if __name__ == "__main__":
    main()