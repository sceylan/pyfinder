# *-* coding: utf-8 *-*
"""
Setup file for the Pybind11 module for libfinder

To compile the module, run the following command:
python setup.py build_ext --inplace
"""
from setuptools import setup, Extension
import pybind11

# Define the extension module
ext_modules = [
    Extension(
        # Module name in Python
        'pylibfinder',

        # Source files that contain your Pybind11 bindings
        ['bindings/pybind11/finite_fault.cpp', 
         ],  
# 'bindings/pybind11/finder.cpp'
        # Includes Pybind11 headers
        include_dirs=[pybind11.get_include()],  
        language='c++',
        extra_compile_args=['-std=c++11'],  # Replace with your C++ version
    ),
]

# Setup function to compile the module
setup(
    name='pylibfinder',
    version='1.0',
    author='Savas Ceylan',
    description='FinDer Pybind11 module',
    ext_modules=ext_modules,
)

