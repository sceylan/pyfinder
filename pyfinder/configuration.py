# -*- encoding: utf-8 -*-
""" Configuration module for pyfinder options and settings. """

class Configuration:
    """ Class for managing the configuration of pyfinder. """
    def __init__(self):
        # Set the default configuration values
        self.config = {
            "use_library": False,
            "library_path": None,
            "executable_path": None
        }

    def set(self, key, value):
        """ Set the configuration value. """
        self.config[key] = value

    def get(self, key):
        """ Get the configuration value. """
        return self.config[key]