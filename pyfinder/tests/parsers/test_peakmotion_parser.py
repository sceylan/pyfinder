# -*- coding: utf-8 -*-
import unittest
import os
import sys
import zipfile
module_path = os.path.dirname(os.path.abspath(__file__))
one_up = os.path.join(module_path, '..')
sys.path.append(one_up)
from clients.services.rrsm.peakmotion_parser import RRSMPeakMotionParser 
from clients.services.peakmotion_data import (PeakMotionStationData, 
                                              PeakMotionChannelData, 
                                              PeakMotionData)

class TestRRSMPeakMotionParser(unittest.TestCase):
    """ Test the parser for RRSM peak motion web service. """
    def test_json(self):
        json_path = os.path.join(
            module_path, 'testdata', 'rrsm-peakmotion.json')
        
        with open(json_path, 'r') as jsonfile:
            parser = RRSMPeakMotionParser()
            parsed_data = parser.parse(jsonfile)

            # data should not be None or empty. The test file
            # contains testomines for a single earthquake.
            self.assertIsNotNone(parsed_data)
            self.assertIsInstance(parsed_data, PeakMotionData)

            for station in parsed_data.get_stations():
                self.assertIsInstance(station, PeakMotionStationData)
                self.assertIn(station.get_station_code(), ['KBN', 'PDG', 'TIR'])

                for channel in station.get_channels():
                    self.assertIsInstance(channel, PeakMotionChannelData)

                    # Test getter methods
                    self.assertIn(channel.get_channel_code(), ['HHN', 'HHE', 'HHZ'])
                    
                    # Test direct access to the internal data dict
                    self.assertIn(channel['channel-code'], ['HHN', 'HHE', 'HHZ'])
            
