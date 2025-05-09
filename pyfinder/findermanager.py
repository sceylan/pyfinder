#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" 
Main module for running the FinDer library wrapper. The FinDerManager 
class is designed to call either FinDer executable directly or the 
library via the bindings. The bindings are in test phase and not yet 
fully implemented.

The FinDerManager class is designed to be used as a command line
utility as well as a runtime library. 
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
from finderutils import (FinderChannelList, FinderSolution)
from utils.dataformatter import (RRSMPeakMotionDataFormatter,
                                 ESMShakeMapDataFormatter,
                                 FinDerFormatterFromRawList,
                                 get_epoch_time)
from utils.station_merger import StationMerger

class FinDerManager:
    """ Class for managing the FinDer library and executable wrappers"""
    def __init__(self, options, configuration=None, metadata=None):
        # Options from the command line arguments
        self.options = options

        if configuration is None:
            # Use the default configuration
            self.configuration = pyfinderconfig
        else:
            # Use the user-defined configuration
            self.configuration = configuration
        
        # Solution metadata mainly for information purposes
        self.metadata = metadata or {}

        # FinDer data directories
        self.finder_temp_data_dir = self.configuration["finder-executable"]["finder-temp-data-dir"]
        self.finder_temp_dir = self.configuration["finder-executable"]["finder-temp-dir"]

        # Working directory
        self.working_dir = None

        # The logger for the FinDerManager
        self.logger = customlogger.file_logger(
            module_name="FinDerManager",
            log_file="finder_manager.log",
            rotate=True,
            overwrite=True,
            level=logging.DEBUG
        )
        
    def set_finder_data_dirs(self, working_dir, finder_event_id):
        """ Set the FinDer data directories using the event id from FinDer run """
        self.finder_temp_data_dir = self.finder_temp_data_dir.replace(
            "{FINDER_RUN_DIR}", working_dir)
        self.finder_temp_dir = self.finder_temp_dir.replace(
            "{FINDER_RUN_DIR}", working_dir)
        
        # Combine the event id with the working directory
        self.finder_temp_data_dir = os.path.join(
            self.finder_temp_data_dir, finder_event_id)
        
        self.logger.info(f"FinDer temp data directory: {self.finder_temp_data_dir}")
        self.logger.info(f"FinDer temp directory: {self.finder_temp_dir}")

    def run(self, event_id=None, file_path=None) -> FinderSolution:
        """ 
        Run the FinDer library based on an event_id or from a file
        event_id has the priority over file_path. The file_path maybe
        more useful for repeated processing of the same data without
        a need to query webservices.

        Returns a FinderSolution object from one of the process_event or 
        process_file methods.
        """
        if event_id:
            # Query the event_id from the web service
            return self.process_event(event_id)
        elif file_path:
            # Use a pre-existing file to execute FinDer. 
            # Useful for offline processing; not yet implemented.
            return self.process_file(file_path)
        else:
            raise ValueError("An event_id or file_path must be provided")

    def process_file(self, file_path) -> FinderSolution:
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
            self.logger.error("No FinDer channel codes to rename. List is empty.")
            return
        
        self.logger.info("Renaming the channel codes in the FinDer output.")        
        
        # Get FinDer's version of data_0 file
        finder_data_0 = os.path.join(self.finder_temp_data_dir, "data_0")
        
        # Check if the file exists
        if not os.path.exists(finder_data_0):
            self.logger.error(f"File {finder_data_0} does not exist. Cannot rename the channel codes.")

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

        self.logger.info(f"Channel codes have been renamed in the FinDer output. New file: {renamed_data_0}")

    def process_event(self, event_id) -> FinderSolution:
        """ Process data associated with an event_id """
        # Check if the event_id is not None
        if not event_id:
            raise ValueError("An event_id must be provided intead of None")
        
        # Create the RRSM and ESM clients
        rrsm_client = RRSMPeakMotionClient()
        _rrsm_code, _rrsm_event, _rrsm_amplitude = rrsm_client.query(event_id=event_id)
        
        esm_client = ESMShakeMapClient()
        _esm_code, _esm_event, _esm_amplitude = esm_client.query(event_id=event_id)
        
        # Is the connection successful?
        if _rrsm_code != 200:
            self.metadata['RRSM_status'] = "Failed: " + str(_rrsm_code)
            raise ConnectionError("Connection to the RRSM web service failed")
        else:
            self.metadata['RRSM_status'] = "Success"

        if _esm_code != 200:
            self.metadata['ESM_status'] = "Failed: " + str(_esm_code)
            raise ConnectionError("Connection to the ESM web service failed")
        else:
            self.metadata['ESM_status'] = "Success"
        
        if _esm_event and _esm_amplitude:
            esm_raw = ESMShakeMapDataFormatter.extract_raw_stations(
                event_data=_esm_event, amplitudes=_esm_amplitude)
        else:
            esm_raw = None

        if _rrsm_event and _rrsm_amplitude:
            rrsm_raw = RRSMPeakMotionDataFormatter.extract_raw_stations(
                event_data=_rrsm_event, amplitudes=_rrsm_amplitude)
        else:
            rrsm_raw = None
            
        # ESM gets the priority over RRSM for event
        _event_data = _esm_event if _esm_event else _rrsm_event

        # Collect more metadata for the solution. The scheduler already 
        # should have dumped some field in the dict:
        # solution_metadata = {
        #         "last_query_time": str(event_meta['last_query_time']),
        #         "delay_until_next_query": delay,}
        self.metadata['origin_time'] = _event_data.get_origin_time()
        self.metadata['longitude'] = _event_data.get_longitude()
        self.metadata['latitude'] = _event_data.get_latitude()
        self.metadata['magnitude'] = _event_data.get_magnitude()
        self.metadata['depth'] = _event_data.get_depth()
        if hasattr(_event_data, "get_magnitude_type"):
            self.metadata['magnitude_type'] = _event_data.get_magnitude_type()
        else:
            self.metadata['magnitude_type'] = ""

        # Merge the raw data if both are available
        if esm_raw and rrsm_raw:
            # Merge the data
            logging.info("Merging the ESM and RRSM data")
            _amplitude_data = StationMerger().merge(esm_data=esm_raw, rrsm_data=rrsm_raw)
        else:
            # Use the raw data from either ESM or RRSM
            _amplitude_data = _esm_amplitude if _esm_amplitude else _rrsm_amplitude

        if self.options["use_library"]:
            # Call the FinDer library wrapper
            from finderlib import FinderLibrary
            library = FinderLibrary(
                options=self.options, configuration=self.configuration).execute(
                    event_data=_event_data, amplitudes=_amplitude_data)
            
            # Return None for the library wrapper. Once implemented, it should return 
            # a FinderSolution object.
            # return True, FinderLibrary.get_finder_solution()
            return None
        
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
            
            from utils.shakemap import ShakeMapExporter
            # from datetime import datetime
            # suffix = datetime.now().strftime("%Y%m%d_%H%M%S")

            # solution = executable.get_finder_solution_object()
            # solution.set_finder_event_id(f"{executable.get_finder_event_id()}_{suffix}")

            smap_exporter = ShakeMapExporter(solution=executable.get_finder_solution_object())
            shakemapexp = smap_exporter.export_all()
            self.logger.info(f"ShakeMap files exported to: {shakemapexp['output_dir']}")

            # Trigger ShakeMap using exported files
            from utils.shakemap import ShakeMapTrigger
            # Create the products directory
            products_dir = os.path.join(shakemapexp["output_dir"], "products")
            os.makedirs(products_dir, exist_ok=True)
            # Copy the ShakeMap files to the products directory
            trigger = ShakeMapTrigger(
                event_id=event_id,
                event_xml=shakemapexp["event.xml"],
                stationlist_path=shakemapexp["stationlist.json"],
                rupture_path=shakemapexp["rupture.json"]  
            )
            trigger.run()

            # Archive the products via ShakeMap exporter under the temp_data directory
            smap_exporter.archive_products(target_base_dir=self.finder_temp_data_dir)

            from services.alert import send_email_with_attachment
            products_dir = os.path.join(shakemapexp["output_dir"], "products")
            attachment = f"{products_dir}/intensity.jpg"
            subject = f"pyFinder Alert - event {event_id}"
            body = f"A new ShakeMap has been produced for event {event_id}.\n"
            send_email_with_attachment(
                subject=subject,
                body=body,
                attachments=[attachment],
                event_id=event_id,
                finder_solution=executable.get_finder_solution_object(),
                metadata=self.metadata
            )

            # Check if the executable was successful            
            # Rename the channel codes if live mode is False. When live mode is False,
            # we pass FinDer only the coordinates and it assigns the channel codes itself.
            # We rename them back to the real ones for debugging purposes.
            if not self.configuration["finder-executable"]["finder-live-mode"]:
                self._rename_channel_codes(executable.get_finder_used_channels())

            # Return the FinderSolution object
            return executable.get_finder_solution_object()
            
        return None
    
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
    solution = manager.run(event_id=options["event_id"])
    if solution is not None:
        print(f"FinDer solution: {solution}")
    else:
        print("No FinDer solution returned.")
