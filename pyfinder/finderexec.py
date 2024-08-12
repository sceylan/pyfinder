# -*- coding: utf-8 -*-
""" Module for executing the FinDer executable, namely the FinDer file. """

import os
import subprocess
import sys


class FinDerExecutable(object):
    """ Class for executing the FinDer executable. """
    def __init__(self, executable_path):
        self.executable_path = executable_path

    def execute(self, data_object):
        """ Execute the FinDer executable. """
        # Check if the executable exists
        if not os.path.exists(self.executable_path):
            raise FileNotFoundError("Could not find the FinDer executable at: {}".format(self.executable_path))

        # Check if the executable is a file
        if not os.path.isfile(self.executable_path):
            raise FileNotFoundError("The FinDer executable path is not a file: {}".format(self.executable_path))

        # Check if the executable is executable
        if not os.access(self.executable_path, os.X_OK):
            raise PermissionError("The FinDer executable is not executable: {}".format(self.executable_path))

        # Execute the FinDer executable
        try:
            # Execute the FinDer executable
            process = subprocess.Popen([self.executable_path], 
                                       stdout=subprocess.PIPE, 
                                       stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            print("FinDer stdout: ", stdout)
            print("FinDer stderr: ", stderr)
        except Exception as e:
            print("Error executing the FinDer executable: ", e)
            sys.exit(1)