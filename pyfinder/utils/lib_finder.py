# *-* coding: utf-8 -*-
""" Utility class for managing the FinDer lbrary"""
import ctypes

class FinderLibrary(object):
    """ Utility class for managing the FinDer lbrary"""
    def __init__(self):
        self._lib = None
        self._lib_path = None

    def load(self, lib_path):
        """ Load the library """
        self._lib_path = lib_path
        self._lib = ctypes.CDLL(lib_path)

        # Return the loaded library
        return self.get_library()

    def get_library(self):
        """ Return the library """
        return self._lib

    def get_library_path(self):
        """ Return the library path """
        return self._lib_path

    def set_library(self, lib):
        """ Set the library """
        self._lib = lib

    def set_library_path(self, lib_path):
        """ Set the library path """
        self._lib_path = lib_path

    def __str__(self):
        return "FinderLibrary(lib_path={})".format(self._lib_path)
    
