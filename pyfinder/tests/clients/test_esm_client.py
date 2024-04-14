# -*- coding: utf-8 -*-
import unittest
from clients import ESMShakeMapClient

class TestESMClient(unittest.TestCase):
    def test_default_contructor(self):
        # Test the constructor with default values. 
        client = ESMShakeMapClient()
        
        self.assertEqual(client.get_agency(), "ESM")
        self.assertEqual(client.get_version(), "1")
        self.assertEqual(client.get_end_point(), "shakemap")
        self.assertEqual(client.get_base_url(), "https://esm-db.eu/esmws/")

    def test_set_url_attributes(self):
        # Test the parts of the query url. 
        client = ESMShakeMapClient()
        client.set_agency("ESM")
        client.set_version("1")
        client.set_end_point("shakemap")
        client.set_base_url("https://esm-db.eu/esmws")
        self.assertEqual(client.get_agency(), "ESM")
        self.assertEqual(client.get_version(), "1")
        self.assertEqual(client.get_end_point(), "shakemap")
        self.assertEqual(client.get_base_url(), "https://esm-db.eu/esmws/")

    def test_query_null_event_id(self):
        # Test the query method. 
        client = ESMShakeMapClient()
        self.assertRaises(ValueError, client.query, event_id=None)

    def test_query(self):
        # Test the query method and returned data. 
        client = ESMShakeMapClient()
        client.query(event_id="20170524_0000045")
        self.assertIsNotNone(client.get_event_data())   
        self.assertIsNotNone(client.get_station_amplitudes())

        # Assert some values from the event data.
        event_data = client.get_event_data()
        self.assertEqual(event_data.get_event_id(), '20170524_0000045')
        self.assertEqual(event_data.get_catalog(), 'EMSC')
        self.assertEqual(event_data.get_network_desc(), 'ESM database')
        self.assertEqual(event_data.get_network_code(), 'ESM')
        
        # Check station names
        station_codes = client.get_station_codes()
        for _sta_name in ['LMS2', 'JAN', 'KASA']:
            self.assertIn(_sta_name, station_codes)

        # Check some station information
        for _sta in client.get_stations():
            self.assertIn(_sta.get_station_name(), ['LMS2', 'JAN', 'KASA'])

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
            
