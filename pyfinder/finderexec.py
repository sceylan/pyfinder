# -*- coding: utf-8 -*-
""" Module for executing the FinDer executable, namely the FinDer file. """

import os
import subprocess
import sys
import json
from utils import customlogger
import pyfinderconfig
from utils.dataformatter import RRSMPeakMotionDataFormatter
from clients.services.peakmotion_data import PeakMotionData


class FinDerExecutable(object):
    """ Class for executing the FinDer executable. """
    def __init__(self, options, configuration):
        # Options from the command line arguments
        self.options = options

        # User-defined configuration
        self.configuration = configuration

        # Path to the FinDer executable
        self.executable_path = self.configuration["finder-executable"]["path"]

        # The logger
        self.logger = None

        # Working directory. It will be created for each event id
        self.working_directory = None

        # Path to the FinDer configuration file
        self.finder_file_config_path = None

    def get_root_output_folder(self):
        """ Get the root output folder from the configuration. """
        output_root_folder = self.configuration["finder-executable"]["output-root-folder"]
        return output_root_folder
    
    def get_working_directory(self):
        """ Get the working directory. Once set, it is the same 
        as combine_event_output_folder() method. """
        return self.working_directory
    
    def initialize_logger(self):
        """ Initialize the logger. """
        log_file = self.configuration["finder-executable"]["log-file-name"]
        overwrite_log_file = self.configuration["logging"]["overwrite-log-file"]
        rotate_log_file = self.configuration["logging"]["rotate-log-file"]

        event_output_folder = self.get_working_directory()

        if log_file is not None:
            log_file = os.path.join(event_output_folder, log_file)
        else:
            # Default log file name, if something goes wrong with the configuration
            log_file = os.path.join(event_output_folder, "pyfinder.log")

        # If overwrite is permitted, remove the existing log file
        if overwrite_log_file and os.path.exists(log_file):
            os.remove(log_file)

        # Create the logger
        self.logger = customlogger.file_logger(
            log_file, overwrite=overwrite_log_file, rotate=rotate_log_file)

        
    def prepare_workspace(self, event_id):
        """ 
        Parepares the working directory and files for running the FinDer executable.
        """
        output_root_folder = self.get_root_output_folder()
        has_write_access = os.access(output_root_folder, os.W_OK)
        
        # Check if the output root folder is a directory and not a file
        if not os.path.isdir(output_root_folder):
           self.logger.error("Terminating! The output root folder is not a directory: {}".format(output_root_folder))
           raise NotADirectoryError("The output root folder is not a directory: {}".format(output_root_folder))
        
        # Check if we have write access to the output root folder
        if not has_write_access:
            print("No write access to the output root folder: {}".format(output_root_folder))

            # Use the current working directory as the output root folder
            previous_output_root_folder = output_root_folder
            output_root_folder = os.path.join(os.getcwd(), "output")

            print(f"No write access to the output root folder: {previous_output_root_folder}")
            print(f"Overriding the root working directory: {output_root_folder}")

        # Check if the output root folder exists
        if not os.path.exists(output_root_folder):
            os.makedirs(output_root_folder)

        # Create a working directory with the event id that is currently being processed
        event_output_folder = os.path.join(output_root_folder, str(event_id))
        if not os.path.exists(event_output_folder):
            os.makedirs(event_output_folder)
        self.working_directory = event_output_folder

        # Initialize the logger
        self.initialize_logger()
        self.logger.info("START... Initiated with '{}'".format(self.options['command_line_args']))
        self.logger.info("Event ID: {}".format(event_id))
        self.logger.info("FinDer executable path: {}".format(self.executable_path))
        self.logger.info("Output root folder: {}".format(output_root_folder))
        
        # Check if we have write access to the event output folder again.
        # We should be OK at this point.
        has_write_access = os.access(event_output_folder, os.W_OK)
        self.logger.debug("Write permission check: {}".format("Access granted" if has_write_access else "Access denied"))
        self.logger.info("Event output folder: {}".format(event_output_folder))
        
        # Dump the configuration to the log file
        self.logger.debug("Self configuration: {}".format(json.dumps(self.configuration, indent=4)))

        # Write the FinDer configuration file
        self.write_finder_configuration()
    
    
    def write_finder_configuration(self):
        """ Write the FinDer configuration file under the working directory. """
        self.logger.info("Writing the FinDer configuration file...")

        try:
            # The template configuration for the FinDer executable (finder_file)
            finder_file_config = pyfinderconfig.finder_file_comfig_template

            # Change the data folder to the working directory. This is where FinDer
            # will create data and temp_data folders to dump its output.
            finder_file_config["DATA_FOLDER"] = self.working_directory

            # Write the configuration to the working directory
            config_file_path = os.path.join(self.working_directory, "finder_file.config")

            with open(config_file_path, "w") as config_file:
                for key, value in finder_file_config.items():
                    config_file.write("{} {}\n".format(key, value))

            self.finder_file_config_path = config_file_path

            # Log the configuration file path
            self.logger.info("FinDer configuration file: {}".format(config_file_path))

            # Log the configuration. Remove json-specific formatting for better readability
            dumps_config = json.dumps(finder_file_config, indent=4)
            dumps_config = dumps_config.replace('"', '').replace(',', '')
            self.logger.debug(f"FinDer configuration: {dumps_config}")
            self.logger.ok("FinDer configuration file is written.")

        except Exception as e:
            self.logger.error("Error writing the FinDer configuration file: {}".format(e))
            raise e

    def check_finder_executable(self):
        # Check if the executable exists
        if not os.path.exists(self.executable_path):
            raise FileNotFoundError("Could not find the FinDer executable at: {}".format(self.executable_path))

        # Check if the executable is a file
        if not os.path.isfile(self.executable_path):
            raise FileNotFoundError("The FinDer executable path is not a file: {}".format(self.executable_path))

        # Check if the executable is executable
        if not os.access(self.executable_path, os.X_OK):
            raise PermissionError("The FinDer executable is not executable: {}".format(self.executable_path))
        
    def write_data_for_finder(self, data_object):
        """ Write the data to the working directory. """
        data_file_path = os.path.join(self.working_directory, "data_0")

        if isinstance(data_object, PeakMotionData):
            out_str = RRSMPeakMotionDataFormatter().format_data(data_object)

        # Write the data to the working directory
        with open(data_file_path, "wb") as data_file:
            data_file.write(out_str)
            
        self.logger.info("Data file written: {}".format(data_file_path))
        return data_file_path

    def execute(self, amplitudes, event_data=None):
        """ Runs the FinDer executable. """
        # Check if the executable exists
        self.check_finder_executable()

        if isinstance(amplitudes, PeakMotionData):
            # RRSM peak motion data contains the event data as well.
            event_data = amplitudes.get_event_data()
        
        # Get the event id to create the working directory
        event_id = event_data.get_event_id()
        
        # Prepare the workspace for the FinDer executable output
        self.prepare_workspace(event_id)

        # Write the data to the working directory
        self.write_data_for_finder(amplitudes)

        try:
            # Execute the FinDer executable
            self.logger.info("Executing the FinDer executable...")

            # Check if the live mode is enabled
            is_live_mode = self.configuration["finder-executable"]["finder-live-mode"]
            if isinstance(is_live_mode, str): 
                if is_live_mode.lower() == "yes":
                    is_live_mode = True
                elif is_live_mode.lower() == "no":
                    is_live_mode = False
                else:
                    is_live_mode = bool(is_live_mode)
            
            if is_live_mode:
                self.logger.info("FinDer live mode is enabled.")
            else:
                self.logger.info("FinDer live mode is disabled.")

            # Command line options for FinDer 
            cmd_line_opt = [self.finder_file_config_path, 
                            self.working_directory, '0', '0', 
                            'yes' if is_live_mode else 'no']
            
            process = subprocess.Popen(
                [self.executable_path] + cmd_line_opt, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE)
            
            stdout, stderr = process.communicate()
            
            # Dump the stdout and stderr to the log file
            self.logger.info("FinDer STDOUT :")
            for line in stdout.decode().splitlines():
                self.logger.finder(line)
            
            if stderr:
                self.logger.warning(">>>> FinDer produced STDERR. See below:")
                for line in stderr.decode().splitlines():
                    self.logger.error(line)
                self.logger.info("<<<< FinDer STDERR: End")
            else:
                self.logger.info(">>>> FinDer STDERR: Empty")
                
        except Exception as e:
            self.logger.error(f"Error executing the FinDer executable: {e}")
            sys.exit(1)

        finally:
            self.logger.info("FINISHED...")
            