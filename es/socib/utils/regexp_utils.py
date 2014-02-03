__author__ = 'ksebastian'
import json


class RegexpUtils:

    EXCLUDED_DIRS_AND_FILES = "../../configuration/excluded_directories_and_files.json"

    DIRECTORIES_AND_FILES = 'directories_and_files'

    # Retrieve the exclude directories and file parts
    json_file = open(EXCLUDED_DIRS_AND_FILES)
    json_data = json.load(json_file)
    json_file.close()


    @staticmethod
    def build_reg_exp():

        reg_exp = ''
        excluded_dirs_and_files = RegexpUtils.json_data[RegexpUtils.DIRECTORIES_AND_FILES]

        if not len(excluded_dirs_and_files):
            return reg_exp

        if len(excluded_dirs_and_files) == 1:
            return excluded_dirs_and_files[0]

        for excluded in excluded_dirs_and_files:
            reg_exp = reg_exp +  excluded + '|'

        reg_exp = reg_exp[0:len(reg_exp) - 1]

        return reg_exp