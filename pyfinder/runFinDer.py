#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" 
Main module for running the FinDer library wrapper. The FinDerManager 
class is designed to call either FinDer executable directly or the 
library via the bindings. The bindings are in test phase and not yet 
fully implemented.
"""
import os
from clients import RRSMPeakMotionClient, RRSMShakeMapClient
import configuration

class FinDerManager:
    """ Class for managing the FinDer library and executable wrappers"""
    def __init__(self, use_library=False):
        # Use the FinDer library or the executable
        self.use_library = use_library

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

    def process_event(self, event_id):
        """ Process data associated with an event_id """
        # Check if the event_id is not None
        if not event_id:
            raise ValueError("An event_id must be provided intead of None")
        
        # Create the RRSM peak motion client
        client = RRSMPeakMotionClient()

        # Query returns a PeakMotionData object, which is the same
        # for amplitude and event data for the RRSM peak motion service.
        _code, _peak_motion_data, _ = client.query(event_id=event_id)
        
        # Is the connection successful?
        if _code != 200:
            raise ConnectionError("Connection to the RRSM web service failed")
        
        if self.use_library:
            # Call the FinDer library wrapper
            from finderlib import FinderLibrary
            FinderLibrary().execute(_peak_motion_data)
        else:
            # Call the FinDer executable
            from finderexec import FinDerExecutable
            FinDerExecutable().execute(_peak_motion_data)

    
def build_args():
    """ Build the command line arguments """
    import argparse

    def verbosity_level(value):
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if value.upper() in levels:
            return value.upper()
        else:
            raise argparse.ArgumentTypeError(f"{value} is not a valid verbosity level. Choose from {', '.join(levels)}.")
    
    parser = argparse.ArgumentParser(description="Run the FinDer wrapper")

    # Add the arguments
    parser.add_argument("--use-lib", help="Flag to use either the FinDer library or executable. "\
                        "If not provided, FinDer executable will be used", default=False,
                        action='store_true')
    
    # Configuration file; required for pyfinder options. If not provided, the default
    # path will be used as ./pyfinder.config
    parser.add_argument("--config", help="Configuration file for pyfinder. Default is ./pyfinder.config", 
                        type=str, required=False)

    # Event id is optional. Defaults to the Kahramanmaras, Turkey event in 2023 for testing
    parser.add_argument("--event-id", help="[Optional] Event ID for processing.", type=str, default=None)
    
    # Test mode; optional. If provided, the test mode will be used with the event-id 20230206_0000008
    parser.add_argument("--test", help="[Optional] Runs in testing mode with event-id 20230206_0000008 (Kahramanmaras, Turkey 2023).", 
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

    # Set the default configuration file, if not provided
    if _args.config is None:
        _args.config = "./pyfinder.config"

    return _args

if __name__ == '__main__':    
    args = build_args()

    print(args)
    # Example usage. Run with the Kahramanmaras event in 2023: 20230206_0000008
    manager = FinDerManager(use_library=args.use_lib)
    manager.run(event_id='20230206_0000008')


