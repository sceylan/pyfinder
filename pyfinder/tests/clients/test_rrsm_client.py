# -*- coding: utf-8 -*-
import unittest
from clients import RRSMShakeMapClient
from clients import RRSMPeakMotionClient

class TestRRSMClient(unittest.TestCase):
    def test_default_contructor(self):
        # Test the constructor with default values. 
        client = RRSMShakeMapClient()
        
        self.assertEqual(client.get_agency(), "ORFEUS")
        self.assertEqual(client.get_version(), "1")
        self.assertEqual(client.get_end_point(), "shakemap")
        self.assertEqual(client.get_base_url(), 
                         "http://orfeus-eu.org/odcws/rrsm/")

    def test_set_url_attributes(self):
        # Test the parts of the query url. 
        client = RRSMShakeMapClient()
        client.set_agency("ORFEUS")
        client.set_version("1")
        client.set_end_point("shakemap")
        client.set_base_url("http://orfeus-eu.org/odcws/rrsm/")
        self.assertEqual(client.get_agency(), "ORFEUS")
        self.assertEqual(client.get_version(), "1")
        self.assertEqual(client.get_end_point(), "shakemap")
        self.assertEqual(client.get_base_url(), 
                         "http://orfeus-eu.org/odcws/rrsm/")

    def test_query_null_event_id(self):
        # Test the query method. 
        client = RRSMShakeMapClient()
        self.assertRaises(ValueError, client.query, event_id=None)

    def test_rrsm_shakemap_query(self):
        # Test the query method and returned data. 
        client = RRSMShakeMapClient()
        client.query(event_id="20170524_0000045")
        self.assertIsNotNone(client.get_station_amplitudes())

        # Check station names
        station_codes = client.get_station_codes()
        for _sta_name in ['KBN', 'PDG', 'TIR']:
            self.assertIn(_sta_name, station_codes)

        # Check some station information
        for _sta in client.get_stations():
            self.assertIn(_sta.get_station_name(), ['KBN', 'PDG', 'TIR'])

            # Check the components for each field.
            for _comp in _sta.get_components():
                self.assertIsNotNone(_comp.get_component_name())
                self.assertIsNotNone(_comp.get_acceleration())
                self.assertIsNotNone(_comp.get_velocity())
                self.assertIsNotNone(_comp.get_psa03())
                self.assertIsNotNone(_comp.get_psa10())
                self.assertIsNotNone(_comp.get_psa30())
                self.assertIsNotNone(_comp.get_acceleration_flag())
                self.assertIsNotNone(_comp.get_velocity_flag())
                self.assertIsNotNone(_comp.get_psa03_flag())
                self.assertIsNotNone(_comp.get_psa10_flag())
                self.assertIsNotNone(_comp.get_psa30_flag())

    def test_rrsm_peakmotions_query(self):
        # Test the query method and returned data. 
        client = RRSMPeakMotionClient()
        client.query(event_id="20170524_0000045")
        self.assertIsNotNone(client.get_station_amplitudes())

        # Check station names
        station_codes = client.get_station_codes()
        for _sta_name in ['KBN', 'PDG', 'TIR']:
            self.assertIn(_sta_name, station_codes)

        # Check some station information
        for _sta in client.get_stations():
            self.assertIn(_sta.get_station_code(), ['KBN', 'PDG', 'TIR'])

            # Check the components for each field.
            for _comp in _sta.get_channels():
                self.assertIsNotNone(_comp.get_channel_code())
                self.assertIsNotNone(_comp.get_acceleration())
                self.assertIsNotNone(_comp.get_velocity())

    def test_rrsm_peakmotions_query_invalid_options(self):
        # Test the query method and returned data. 
        client = RRSMPeakMotionClient()
        client.query(event_id="20170524_0000045", type="event")

        # The type option should be eliminated internally from the query
        # as it is not a valid option for the peak motion web service.
        url = client.get_web_service().get_combined_url()
        self.assertEqual(url, "http://orfeus-eu.org/odcws/rrsm/1/peak-motion?eventid=20170524_0000045")
        
        # Check eveything is in place after the removal of the invalid option.
        self.assertIsNotNone(client.get_station_amplitudes())

        # Check station names
        station_codes = client.get_station_codes()
        for _sta_name in ['KBN', 'PDG', 'TIR']:
            self.assertIn(_sta_name, station_codes)

        # Check some station information
        for _sta in client.get_stations():
            self.assertIn(_sta.get_station_code(), ['KBN', 'PDG', 'TIR'])

            # Check the components for each field.
            for _comp in _sta.get_channels():
                self.assertIsNotNone(_comp.get_channel_code())
                self.assertIsNotNone(_comp.get_acceleration())
                self.assertIsNotNone(_comp.get_velocity())
                