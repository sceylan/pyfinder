#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" 
Main module for running the FinDer library wrapper. The FinDerManager 
class is designed to call either FinDer executable directly or the 
library via the bindings. The bindings are in test phase and not yet 
fully implemented.
"""
import os
import sys
import logging
from pyfinderconfig import pyfinderconfig
from utils import customlogger
from clients import (RRSMPeakMotionClient, 
                     RRSMShakeMapClient,
                     EMSCFeltReportClient,
                     ESMShakeMapClient)
from finderutils import FinderChannelList

class FinDerManager:
    """ Class for managing the FinDer library and executable wrappers"""
    def __init__(self, options, configuration):
        # Options from the command line arguments
        self.options = options

        # User-defined configuration
        self.configuration = configuration

        # FinDer data directories
        self.finder_temp_data_dir = configuration["finder-executable"]["finder-temp-data-dir"]
        self.finder_temp_dir = configuration["finder-executable"]["finder-temp-dir"]

        # Working directory
        self.working_dir = None

    def set_finder_data_dirs(self, working_dir, finder_event_id):
        """ Set the FinDer data directories using the event id from FinDer run """

        self.finder_temp_data_dir = self.finder_temp_data_dir.replace(
            "{FINDER_RUN_DIR}", working_dir)
        self.finder_temp_dir = self.finder_temp_dir.replace(
            "{FINDER_RUN_DIR}", working_dir)
        
        # Combine the event id with the working directory
        self.finder_temp_data_dir = os.path.join(
            self.finder_temp_data_dir, finder_event_id)
        
        
        logging.info(f"FinDer temp data directory: {self.finder_temp_data_dir}")
        logging.info(f"FinDer temp directory: {self.finder_temp_dir}")

    def run(self, event_id=None, file_path=None):
        """ 
        Run the FinDer library based on an event_id or from a file
        event_id has the priority over file_path. The file_path maybe
        more useful for repeated processing of the same data without
        a need to query webservices.
        """
        if event_id:
            self.process_event(event_id)
        elif file_path:
            self.process_file(file_path)
        else:
            raise ValueError("An event_id or file_path must be provided")

    def process_file(self, file_path):
        """ Read data from a file and process it """
        raise NotImplementedError(
            "FinDerManager.process_file() method is not implemented yet")

    
    def _rename_channel_codes(self, finder_used_channels: FinderChannelList):
        """ 
        Rename the channel codes with the real ones in the FinDer output 
        by matching the coordinates. This is performed when live_mode is
        False, where FinDer assigns channel/station codes itself. 
        """
        if not finder_used_channels or len(finder_used_channels) == 0:
            logging.error("No FinDer channel codes to rename. List is empty.")
            return
        
        logging.info("Renaming the channel codes in the FinDer output.")        
        
        # Get FinDer's version of data_0 file
        finder_data_0 = os.path.join(self.finder_temp_data_dir, "data_0")
        
        # Check if the file exists
        if not os.path.exists(finder_data_0):
            logging.error(f"File {finder_data_0} does not exist. Cannot rename the channel codes.")

        # Read the FinDer data_0 file
        stations = {
            "lat": [],
            "lon": [],
            "sncl": [],
            "timestamp": [],
            "pga": []
        }
        header = "# "
        with open(finder_data_0, 'r') as f:
            lines = f.readlines()

            # Read the header
            header = lines[0]

            # And the data
            lines = lines[1:]
    
            for line in lines:
                _line = line.strip().split()
                stations['lat'].append(float(_line[0]))
                stations['lon'].append(float(_line[1]))
                
                # Find this station in the used channels
                for _channel in finder_used_channels:
                    if _channel.get_latitude() == float(_line[0]) and \
                        _channel.get_longitude() == float(_line[1]):
                        # Replace the channel code
                        _line[2] = _channel.get_sncl()
                        break

                stations['sncl'].append(_line[2])
                stations['timestamp'].append(_line[3])
                stations['pga'].append(float(_line[4]))

        # Write the new data_0 file
        renamed_data_0 = os.path.join(self.finder_temp_data_dir, "data_0_renamed")
        with open(renamed_data_0, 'w') as f:
            f.write(header)
            for i in range(len(stations['lat'])):
                f.write(f"{stations['lat'][i]}  {stations['lon'][i]}  {stations['sncl'][i]}  " + \
                        f"{stations['timestamp'][i]} {stations['pga'][i]}\n")

        logging.info(f"Channel codes have been renamed in the FinDer output. New file: {renamed_data_0}")

    def process_event(self, event_id):
        """ Process data associated with an event_id """
        # Check if the event_id is not None
        if not event_id:
            raise ValueError("An event_id must be provided intead of None")
        
        # Create the RRSM peak motion client
        # client = RRSMPeakMotionClient()
        # _code, _event_data, _amplitude_data = client.query(event_id=event_id)
        
        client = ESMShakeMapClient()
        _code, _event_data, _amplitude_data = client.query(event_id=event_id)
        
        # Is the connection successful?
        if _code != 200:
            raise ConnectionError("Connection to the RRSM web service failed")
        
        if self.options["use_library"]:
            # Call the FinDer library wrapper
            from finderlib import FinderLibrary
            FinderLibrary(options=self.options, configuration=self.configuration).execute(
                event_data=_event_data, amplitudes=_amplitude_data)
        else:
            # Call the FinDer executable
            from finderexec import FinDerExecutable
            executable = FinDerExecutable(
                options=self.options, configuration=self.configuration).execute(
                    event_data=_event_data, amplitudes=_amplitude_data)
            
            # Set the FinDer data directories
            self.working_dir = executable.get_working_directory()
            self.set_finder_data_dirs(working_dir=executable.get_working_directory(), 
                                      finder_event_id=executable.get_finder_event_id())
            
            # Rename the channel codes if live mode is False
            if not self.configuration["finder-executable"]["finder-live-mode"]:
                self._rename_channel_codes(executable.get_finder_used_channels())
            

    
def build_args():
    """ Build the command line arguments """
    import argparse

    def verbosity_level(value):
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if value.upper() in levels:
            return value.upper()
        else:
            raise argparse.ArgumentTypeError(
                f"{value} is not a valid verbosity level. Choose from {', '.join(levels)}.")
            
    parser = argparse.ArgumentParser(description="Run the FinDer wrapper")

    # Add the arguments
    parser.add_argument("--use-lib", help="Flag to use either the FinDer library or executable. "\
                        "If not provided, FinDer executable will be used", default=False,
                        action='store_true')
    
    # Event id is optional. Defaults to the Kahramanmaras, Turkey event in 2023 for testing
    parser.add_argument("--event-id", help="[Optional] Event ID for processing.", type=str, default=None)
    
    # Test mode; optional. If provided, the test mode will be used with the test event
    parser.add_argument("--test", help="[Optional] Runs in testing mode with the test event as defined in configuration.", 
                        default=False, action='store_true')
    
    # SeisComp support; optional. If provided, the results will be dumped in the SeisComp database.
    parser.add_argument("--with-seiscomp", help="[Optional] Dump the results in the SeisComp database.",
                        default=False, action='store_true')
                         
    # Logging options
    parser.add_argument("--verbosity", help="Logging level for the application. Default is INFO", 
                        type=verbosity_level, default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
    
    parser.add_argument("--log-file", help="Log file path", type=str, default=None)

    # Parse the arguments
    _args = parser.parse_args()

    return _args

if __name__ == '__main__':    
    # Get the command line arguments
    args = build_args()

    # If no arguments are provided, print the help message
    if len(sys.argv) == 1:
        print("No arguments provided. Use the -h option for help.")
        sys.exit(1)

    # Set the options from the command line arguments
    options = {
        "verbosity": args.verbosity,
        "log_file": args.log_file,
        "with_seiscomp": args.with_seiscomp,
        "event_id": args.event_id,
        "test": args.test,
        "use_library": args.use_lib
    }

    # Override with the command line log file, if provided
    log_file = pyfinderconfig["finder-executable"]["log-file-name"]
    if options["log_file"] is not None:
        pyfinderconfig["finder-executable"]["log-file-name"] = options["log_file"]

    # Store the whole command line in the options as one string
    options["command_line_args"] = f"{sys.argv[0]} " + \
        " ".join([f"--{key} {value}" for key, value in options.items()])
    
    # If the test mode is enabled, set the event_id to the test event
    if options["test"]:
        options["event_id"] = pyfinderconfig["general"]["test-event-id"]
    
    # Execute the FinDer manager, which will call either the FinDer library 
    # or executable based on the options
    manager = FinDerManager(options=options, configuration=pyfinderconfig)
    manager.run(event_id=options["event_id"])

