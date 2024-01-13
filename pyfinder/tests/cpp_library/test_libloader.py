import os
import sys
import unittest
import subprocess
import ctypes
module_path = os.path.dirname(os.path.abspath(__file__))
one_up = os.path.join(module_path, '..')
sys.path.append(one_up)
from utils import FinderLibrary

def compile(libpath):
    # Compile the C++ code to create a shared library 
    compile_command = ["g++", "-shared", "-fPIC", 
                       os.path.join(libpath, "libtest.cpp"), 
                       "-o", os.path.join(libpath, "libtest.so")]
    subprocess.run(compile_command, check=True)


class TestFinderLibrary(unittest.TestCase):
    def test_cpp_lib_loader(self):
        # Test cpp library loading
        # Compile the C++ code to create a shared library
        lib_path = os.path.join(os.path.dirname(__file__), "lib")
        if os.path.exists(os.path.join(lib_path, "libtest.so")):
            os.remove(os.path.join(lib_path, "libtest.so"))
        compile(lib_path)
        
        # Load the library
        cpp_lib_path = os.path.join(lib_path, "libtest.so")
        finder_lib = FinderLibrary()
        finder_lib.load(cpp_lib_path)
        lib = finder_lib.get_library()
        self.assertIsNotNone(lib)
       
        self.a, self.b = 3, 4
        a_ptr = ctypes.byref(ctypes.c_int(self.a))
        b_ptr = ctypes.byref(ctypes.c_int(self.b))
        result = lib.sum(a_ptr, b_ptr)
        
        self.assertTrue(isinstance(result, int))
        self.assertEqual(result, self.a + self.b)

        # Clean up
        os.remove(os.path.join(lib_path, "libtest.so"))

