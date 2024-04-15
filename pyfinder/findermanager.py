#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from clients import RRSMPeakMotionClient, RRSMShakeMapClient
from libfinder import FinderLibrary

class FinDerManager:
    """ Class for managing the FinDer library wrapper"""
    def __init__(self):
        pass

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
        
        # # Create the RRSM peak motion client
        # client = RRSMPeakMotionClient()

        # print(client.get_url())
        # # Query returns a PeakMotionData object, which is the same
        # # for amplitude and event data for the RRSM peak motion service.
        # _code, _peak_motion_data, _ = client.query(event_id=event_id)
        
        # print(_peak_motion_data.get_event_data())
        # for _station in _peak_motion_data.get_stations():
        #     print(_station)

        # Call the FinDer library
        _peak_motion_data = None
        FinderLibrary().execute(_peak_motion_data)

    
if __name__ == '__main__':    
    # Example usage. Run with the Kahramanmaras event in 2023: 20230206_0000008
    manager = FinDerManager()
    manager.run(event_id='20230206_0000008')


