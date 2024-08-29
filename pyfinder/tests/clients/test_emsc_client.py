# -*- coding: utf-8 -*-
import unittest
from clients import EMSCFeltReportClient

class TestESMClient(unittest.TestCase):
    def test_default_contructor(self):
        # Test the constructor with default values. 
        client = EMSCFeltReportClient()
        
        self.assertEqual(client.get_agency(), "EMSC")
        self.assertEqual(client.get_version(), "1.1")
        self.assertEqual(client.get_end_point(), "api")
        self.assertEqual(client.get_base_url(), "https://www.seismicportal.eu/testimonies-ws/")

    def test_set_url_attributes(self):
        # Test the parts of the query url. 
        client = EMSCFeltReportClient()
        client.set_agency("EMSC")
        client.set_version("1.1")
        client.set_end_point("api")
        client.set_base_url("https://www.seismicportal.eu/testimonies-ws/")
        self.assertEqual(client.get_agency(), "EMSC")
        self.assertEqual(client.get_version(), "1.1")
        self.assertEqual(client.get_end_point(), "api")
        self.assertEqual(client.get_base_url(), "https://www.seismicportal.eu/testimonies-ws/")

    def test_query_null_event_id(self):
        # Test the query method. 
        client = EMSCFeltReportClient()
        self.assertRaises(ValueError, client.query, event_id=None)

    def test_query(self):
        # Test the query method and returned data. 
        client = EMSCFeltReportClient()
        code, _, _ = client.query(event_id='20161030_0000029')

        if code != 200:
            self.skipTest("The web service is not available.")
            
        event_data = client.get_event_data()

        self.assertIsNotNone(event_data.get_event_deltatime())
        self.assertIsNotNone(event_data.get_event_id())
        self.assertIsNotNone(event_data.get_latitude())
        self.assertIsNotNone(event_data.get_longitude())
        self.assertIsNotNone(event_data.get_magnitude())
        self.assertIsNotNone(event_data.get_magnitude_type())
        self.assertIsNotNone(event_data.get_event_time())
        self.assertIsNotNone(event_data.get_depth())
        self.assertIsNotNone(event_data.get_event_nbtestimonies())
        self.assertIsNotNone(event_data.get_event_region())
        self.assertIsNotNone(event_data.get_event_last_update())

        intensities = client.get_feltreports()
        self.assertIsNotNone(intensities)
        self.assertEqual(intensities.get_event_id(), "20170919_0000091")
        self.assertIsNotNone(intensities.get_intensities())
