# *-* coding: utf-8 *-*
"""
Setup file for the Pybind11 module for libfinder

To compile the module, run the following command:
python setup.py build_ext --inplace
"""
from setuptools import setup
from pybind11.setup_helpers import Pybind11Extension, build_ext

# Define the extension module with Pybind11Extension
ext_modules = [
    Pybind11Extension(
        # Module name in Python
        'pylibfinder',  

        # Source files
        ['bindings/pybind11/finite_fault.cpp', 'bindings/pybind11/finder.cpp'],  

        # Mention specifically the C++
        language='c++'
    ),
]

# Setup function to compile the module
setup(
    name='pylibfinder',
    version='1.0',
    author='Savas Ceylan',
    description='FinDer Pybind11 module',
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},  # Important for proper building
    zip_safe=False,
)

