import sys
sys.path.append("/home/ksebastian/workspace/netcdf-utils/")

from es.socib.utils.regexp_utils import RegexpUtils

__author__ = 'ksebastian'

import logging
import logging.config
from numpy import *
from es.socib.netcdf.modification_tools import NetcdfUpdater
import os
import re


def main():
    """
    """

    LOG_CONFIG_FILE = '../../configuration/log.conf'
    logging.config.fileConfig(LOG_CONFIG_FILE, disable_existing_loggers=False)
    logger = logging.getLogger("netcdf_utils")

    remove_element = dict({
        "global_attributes": set(),
        "variables": set(["DEPTH_ADCP3", "CUR_SPE", "CUR_DIR", "VEL_EAS", "VEL_UPW", "VEL_NOR", "WTR_AMP_BEAM1",
                          "WTR_AMP_BEAM2", "WTR_AMP_BEAM3"]),
        "dimensions": set(["depth_adcp3"])
    })

    # Create the parameters dictionary
    parameters = dict()
    parameters['remove_element'] = remove_element
    # parameters['netcdf_canonical_path'] = netcdf_canonical_path
    # parameters['new_variables_data'] = new_variables_data
    # parameters['new_global_attributes'] = new_global_attributes
    # parameters['new_variable_attributes'] = new_variable_attributes

    base_dir = '/data/current/opendap/observational/mooring/waves_recorder/'
    # base_dir = '/home/ksebastian/opendap/observational/mooring/waves_recorder/'

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

            parameters['netcdf_canonical_path'] = f

            NetcdfUpdater.modify_netcdf_file(**parameters)

            logger.info('Updated NetCDF file ' + f)


if __name__ == "__main__":
    main()