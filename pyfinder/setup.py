# *-* coding: utf-8 *-*
"""
Setup file for the Pybind11 module for libfinder

To compile the module, run the following command for a clean and verbose build:
python3 setup.py build_ext --inplace --force -v
"""
from setuptools import setup
import pybind11
from pybind11.setup_helpers import Pybind11Extension, build_ext

# Define the extension module with Pybind11Extension
ext_modules = [
    Pybind11Extension(
        # Module name in Python
        'pylibfinder',  

        # Source files
        ['bindings/pybind11/finite_fault.cpp'],  

        # Include directories. gmt headers are needed by FinDer
        include_dirs=[
            pybind11.get_include(), '/usr/include/opencv', '/usr/include/gmt/', '/opt/seiscomp/include/'],

        # Libraries to link: Provide the path to the Finder, opencv, SeisComp and GMT libraries
        # The Library name should be without the 'lib' prefix and the '.so' suffix
        # library_dirs=['/usr/local/lib', '/opt/seiscomp/lib/', '/usr/lib/x86_64-linux-gnu/'],
        library_dirs=['/usr/local/src/app/FinDer/libsrc', '/opt/seiscomp/lib/', '/usr/lib/x86_64-linux-gnu/'],
        libraries=['Finder', 
                   'seiscomp_core', 'seiscomp_config', 'seiscomp_daplugin', 
                   'opencv_core', 'opencv_imgproc', 'opencv_highgui', 'gmt'],
        
        # Mention specifically the C++
        language='c++'
    ),
]

# Setup function to compile the module
setup(
    name='pylibfinder',
    version='0.0.1',
    author='Savas Ceylan',
    description='FinDer Pybind11 bindings module',
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},  
    # Debugging options
    extra_compile_args=['-g', '-O0'],
    zip_safe=False,
)

