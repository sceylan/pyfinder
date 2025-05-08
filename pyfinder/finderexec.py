# -*- coding: utf-8 -*-
""" Module for executing the FinDer executable, namely the FinDer file. """

import os
import subprocess
import sys
import json
from typing import List
from datetime import datetime
from utils import customlogger
import pyfinderconfig
from clients.services.peakmotion_data import PeakMotionData
from clients.services.shakemap_data import ShakeMapStationAmplitudes
from finderutils import (FinderChannelList, FinderChannel, 
                         FinderSolution, FinderRupture,
                         FinderEvent)
from finderutils import (read_event_solution_from_file, 
                         read_rupture_polygon_from_file,
                         read_finder_channels_from_file)
from utils.dataformatter import (RRSMPeakMotionDataFormatter,
                                 ESMShakeMapDataFormatter,
                                 FinDerFormatterFromRawList,
                                 get_epoch_time)
from utils.station_merger import RawStationMeasurement

class FinDerExecutable(object):
    """ Class for executing the FinDer executable. """
    def __init__(self, options: dict, configuration: dict):
        # Options from the command line arguments
        self.options: dict = options

        # User-defined configuration
        self.configuration: dict = configuration

        # Path to the FinDer executable
        self.executable_path: str = self.configuration["finder-executable"]["path"]

        # The logger
        self.logger = None

        # Working directory. It will be created for each event id
        self.working_directory: str = None

        # Path to the FinDer configuration file
        self.finder_file_config_path: str = None

        # Event ID used by the FinDer executable
        self.finder_event_id: str = None

        # Channels used by the FinDer executable
        self.finder_used_channels: FinderChannelList = None

        # FinDer solution (channels used, rupture, event)
        self.finder_solution: FinderSolution = None

    def get_finder_solution_object(self):
        """ Get the FinDer solution object. """
        return self.finder_solution

    def get_finder_event_id(self):
        """ Get the event id used by the FinDer executable. """
        return self.finder_event_id
    
    def get_configured_root_folder(self):
        """ Get the root output folder from the configuration. """
        return self.configuration["finder-executable"]["output-root-folder"]
            
    def get_working_directory(self):
        """ Get the working directory. Once set, it is the same 
        as combine_event_output_folder() method. """
        return self.working_directory
    
    def get_finder_used_channels(self) -> FinderChannelList:
        """ Get the channels used by the FinDer executable. """
        return self.finder_used_channels
    
    def _initialize_logger(self):
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

        # Create the logger
        self.logger = customlogger.file_logger(
            log_file=log_file, module_name="pyfinder", 
            overwrite=overwrite_log_file, rotate=rotate_log_file)

    def _prepare_workspace(self, event_id):
        """ 
        Parepares the working environment for running the FinDer executable.
        FinDer needs a working directory to write its output and a specific
        config file configured for this event.
        """
        output_root_folder = self.get_configured_root_folder()
        has_write_access = os.access(output_root_folder, os.W_OK)
        
        # Check if the output root folder is a directory and not a file
        if not os.path.isdir(output_root_folder):
           self.logger.error("Terminating! The output root folder is not a directory: {}".format(output_root_folder))
           raise NotADirectoryError("The output root folder is not a directory: {}".format(output_root_folder))
        
        # Check if we have write access to the output root folder
        is_workdir_overriden = False
        if not has_write_access:
            # Use ~/pyfinder-output as the default output folder
            output_root_folder = os.path.join(os.path.expanduser("~"), "pyfinder-output")
            is_workdir_overriden = True

        # Check if the output root folder exists
        if not os.path.exists(output_root_folder):
            os.makedirs(output_root_folder)

        # Create a working directory with the event id that is currently being processed
        self.working_directory = os.path.join(output_root_folder, str(event_id))
        if not os.path.exists(self.working_directory):
            os.makedirs(self.working_directory)
        
        # Initialize the logger with a log file inside the working directory
        self._initialize_logger()
        self.logger.info("START... Initiated with '{}'".format(self.options['command_line_args']))
        self.logger.info("Event ID: {}".format(event_id))
        self.logger.info("FinDer executable path: {}".format(self.executable_path))
        self.logger.info("Output root folder: {}".format(output_root_folder))

        if is_workdir_overriden:
            # Log a warning if the output root folder is overriden due 
            # to write permission issues
            self.logger.warning(f"No write access to the configured output root folder: " + \
                                f"{self.get_configured_root_folder()}")
            self.logger.warning(f"Your path is overriden!")
            
        # Check if we have write access to the event output folder again.
        # We should be OK at this point.
        has_write_access = os.access(self.working_directory, os.W_OK)
        self.logger.debug("Write permission check: {}".format
                          ("Access granted" if has_write_access else "Access denied"))
        self.logger.info("Event output folder: {}".format(self.working_directory))
        
        # Dump the configuration to the log file
        self.logger.debug("Self configuration: {}".format(json.dumps(self.configuration, indent=4)))

        # Write the FinDer configuration file
        self._write_finder_configuration()
    
    
    def _write_finder_configuration(self):
        """ Write the FinDer configuration file under the working directory. """
        self.logger.info("Writing the FinDer configuration file...")

        try:
            # The template configuration for the FinDer executable (finder_file)
            finder_file_config = pyfinderconfig.finder_file_config_template

            # Change the data folder to the working directory. This is where FinDer
            # will create 'temp' and 'temp_data' directories to dump its output.
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

    def _check_finder_executable(self):
        # Check if the executable exists
        if not os.path.exists(self.executable_path):
            raise FileNotFoundError("Could not find the FinDer executable at: {}".format(self.executable_path))

        # Check if the executable is a file
        if not os.path.isfile(self.executable_path):
            raise FileNotFoundError("The FinDer executable path is not a file: {}".format(self.executable_path))

        # Check if the executable is executable
        if not os.access(self.executable_path, os.X_OK):
            raise PermissionError("The FinDer executable is not executable: {}".format(self.executable_path))
        
    def _write_data_for_finder(self, amplitudes, event_data):
        """ Write the data to the working directory. """
        data_file_path = os.path.join(self.working_directory, "data_0")

        if isinstance(amplitudes, PeakMotionData):
            # RRSM peak motion data contains the event data as well.
            # Amplitudes and event data are the same for the RRSM peak motion service.
            out_str, finder_stations = RRSMPeakMotionDataFormatter().format_data(
                amplitudes=amplitudes, event_data=amplitudes)
            
        elif isinstance(amplitudes, ShakeMapStationAmplitudes):
            out_str, finder_stations = ESMShakeMapDataFormatter().format_data(
                amplitudes=amplitudes, event_data=event_data)
            
        elif isinstance(amplitudes, List) or isinstance(amplitudes, list):   
            self.logger.info("Merged ESM+RRSM data has been passed to FinDer.")
            # Format the merged data for FinDer   
            out_str, finder_stations = FinDerFormatterFromRawList.format(
                event_lat=event_data.get_latitude(),
                event_lon=event_data.get_longitude(),
                event_depth_km=event_data.get_depth(),
                event_mag=event_data.get_magnitude(),
                event_time_epoch=get_epoch_time(event_data.get_origin_time()),
                station_list=amplitudes
            )

        # Write the data to the working directory
        with open(data_file_path, "wb") as data_file:
            data_file.write(out_str)
            
        self.logger.info("Data file written: {}".format(data_file_path))
        return data_file_path, finder_stations


    def _is_live_mode_on(self):
        """ Checks if the live mode is enabled. """
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
    
    
    def _process_finder_output(self, stdout, stderr):
        """ Process the FinDer output for the Event_ID and log everything. """
        self.logger.info(">>>> Start of FinDer::STDOUT")
        
        for line in stdout.decode().splitlines():
            self.logger.finder(line)

            # Get the Event ID from the FinDer output. FinDer used 
            # a time stamp as the event ID in the output.
            if "Event_ID" in line:
                event_id = line.split("=")[-1].strip()
                self.finder_event_id = event_id

        self.logger.info("<<<< End of FinDer::STDOUT")

        # Log the event ID used by the FinDer executable
        self.logger.debug(f"-"*80)
        self.logger.debug(f"FinDer Event ID used for output: {self.finder_event_id}")
        if self.finder_event_id is None:
            self.logger.ERROR("FinDer did not return an event ID. Check the output for errors.")
        self.logger.debug(f"-"*80)

        # Log the stderr if there are any
        if stderr:
            self.logger.warning(">>>> FinDer produced errors/warnings! See FinDer::STDERR below.")
            for line in stderr.decode().splitlines():
                self.logger.error(line)
            self.logger.info("<<<< End of FinDer::STDERR")
        else:
            self.logger.info(">>>> FinDer::STDERR: Empty")
        

    def _run_finder(self):
        """ Run the FinDer executable. """
        self.logger.info("Executing the FinDer executable...")

        # Check if the live mode is enabled
        is_live_mode = self._is_live_mode_on()

        # Command line options for FinDer 
        cmd_line_opt = [self.finder_file_config_path, 
                        self.working_directory, '0', '0', 
                        'yes' if is_live_mode else 'no']
            
        process = subprocess.Popen(
            [self.executable_path] + cmd_line_opt, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE)
            
        stdout, stderr = process.communicate()

        # Handle the output to log and learn the event ID
        # that FinDer assinged for the output. This event ID
        # will be used to combine a path to the event folder.
        self._process_finder_output(stdout, stderr)

        # Check if the process is successful
        if process.returncode != 0:
            self.logger.error(f"FinDer execution failed with return code: {process.returncode}")
            self.logger.error(f"Check the log file for more details: {self.logger.log_file}")
            sys.exit(1)

        # Return the stdout, stderr, and the return code, although we don't need them
        return stdout, stderr, process.returncode
        
    def _collect_finder_output(self, event_id):
        """ Collect the FinDer output. """
        self.logger.info("Collecting the FinDer output...")
        
        # Folder where the FinDer output is stored:
        # <output_root_folder>/<event_id>/temp_data/<finder_event_id>
        event_output_folder = os.path.join(
            self.working_directory, "temp_data", self.finder_event_id)
         
        # Create a FinderSolution object to store the FinDer output
        self.finder_solution = FinderSolution()
        self.finder_solution.set_finder_event_id(self.get_finder_event_id())
        self.finder_solution.set_event_id(event_id)

        # Read the FinDer output files
        event_file = os.path.join(event_output_folder, "core_info_0")
        event_solution = read_event_solution_from_file(event_file)

        rupture_file = os.path.join(event_output_folder, "finder_rupture_list_0")
        rupture_polygon = read_rupture_polygon_from_file(rupture_file)
        
        finder_channels_file = os.path.join(event_output_folder, "data_0")
        finder_channels = read_finder_channels_from_file(finder_channels_file)

        # Store the FinDer solution
        self.finder_solution.set_event(event_solution)
        self.finder_solution.set_rupture(rupture_polygon)
        self.finder_solution.set_channels(finder_channels)

        # Log the FinDer solution
        self.logger.info("FinDer solution is collected.")
        self.logger.info(f"{self.finder_solution}")
        self.logger.info("FinDer solution is stored in the FinderSolution object.")

    def execute(self, amplitudes, event_data):
        """ Runs the FinDer executable. Entry point for the class. """
        # The start time of the execution
        _exec_start = datetime.now()

        # Check if the executable exists
        self._check_finder_executable()

        if isinstance(amplitudes, PeakMotionData):
            # RRSM peak motion data contains the event information as well.
            event_data = amplitudes.get_event_data()
        
        # Get the event id to create the working directory
        event_id = event_data.get_event_id()
        
        # Prepare the workspace for the FinDer executable output
        self._prepare_workspace(event_id)

        # Write the data to the working directory
        my_data0_path, self.finder_used_channels = \
            self._write_data_for_finder(amplitudes, event_data)
        
        try:
            # Execute the FinDer executable
            self._run_finder()
            
        except Exception as e:
            # Log the error and exit
            self.logger.error(f"Error executing FinDer:")
            self.logger.error(f"{e}")
            sys.exit(1)

        else:
            # Log the success and collect the output
            self.logger.info(f"FinDer execution is successful.")
            self._collect_finder_output(event_id=event_id)

        finally:
            # The end of the execution
            _exec_end = datetime.now()
            _exec_time = _exec_end - _exec_start
            _exec_time_min = round(_exec_time.total_seconds() / 60, 2)

            self.logger.info(f"execute() FINISHED... Elapsed time is {_exec_time} ({_exec_time_min} minutes)")

        # Return the self object for further use
        return self
            