#!/usr/bin/env python
from setuptools import setup, find_packages
import os


# Utility function to read the README file. Used for the long_description.
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='netcdf_extended_utils',
    version='0.1',
    description='Extended netcdf utils to modify NetCDF files',
    long_description=read('README'),
    license='GNU',
    author='Kristian Sebastian',
    author_email='data.centre@socib.es',
    url='',
    packages=find_packages(),
    packages_data={'netcdf_extended_utils':['configuration/*']}
)
