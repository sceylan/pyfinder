# -*- coding: utf-8 -*-
"""Unit tests for the base client class."""
import unittest
from clients.services import RRSMShakeMapWebService

class TestRRSMShakeMapWebService(unittest.TestCase):
    """Unit tests for the RRSM Shakemap web service client."""
    def test_url_build(self):
        # Test the build_url method.
        client = RRSMShakeMapWebService()
        client.set_version("1")
        client.set_end_point("shakemap")
        client.set_base_url("http://orfeus-eu.org/odcws/rrsm/")
        url = client.build_url()
        self.assertEqual(url, "http://orfeus-eu.org/odcws/rrsm/1/shakemap?")

    def test_supported_options(self):
        # Test the get_supported_options method.
        client = RRSMShakeMapWebService()
        options = client.get_supported_options()
        self.assertEqual(options, ['eventid', 'type'])

    def test_url_build_with_valid_options(self):
        # Test the build_url method with valid, several options.
        client = RRSMShakeMapWebService()
        client.set_version("1")
        client.set_end_point("shakemap")
        client.set_base_url("http://orfeus-eu.org/odcws/rrsm/")
        url = client.build_url(eventid="test_id")
        self.assertEqual(
            url, "http://orfeus-eu.org/odcws/rrsm/1/shakemap?eventid=test_id")


    def test_query_with_supported_options(self):
        # Test the query method.
        client = RRSMShakeMapWebService()
        client.set_agency("ORFEUS")
        client.set_version("1")
        client.set_end_point("shakemap")
        client.set_base_url("http://orfeus-eu.org/odcws/rrsm/")
        url = client.build_url(eventid='20170524_0000045')
        code, data = client.query(url=url)
        
        # Check the query against common error codes. 
        if code != 503:
            # Service is avaliable, so these error should not be returned
            # if data is not removed from the ESM server. In that case, the
            # error code will be 404.
            for _code in [400, 404, 500, 501, 502]:
                self.assertNotEqual(code, _code)

        # Check the data
        self.assertIsNotNone(data)
        
        # Check the data content
        self.assertEqual(data.get_stations()[0].get('code'), 'KBN')

        # Check the URL
        self.assertEqual(url, "http://orfeus-eu.org/odcws/rrsm/1/"
                         "shakemap?eventid=20170524_0000045")

    def test_query_with_unsupported_options(self):
        # Test the query method.
        client = RRSMShakeMapWebService()
        client.set_agency("ORFEUS")
        client.set_version("1")
        client.set_end_point("shakemap")
        client.set_base_url("http://orfeus-eu.org/odcws/rrsm/")
        url = client.build_url(eventid='20170524_0000045', 
                               catalog='EMSC', format='event_dat')
        code, data = client.query(url=url)
        
        # Check the query against common error codes. 
        if code != 503:
            # Service is avaliable, so these error should not be returned
            # if data is not removed from the ESM server. In that case, the
            # error code will be 404.
            for _code in [400, 404, 500, 501, 502]:
                self.assertNotEqual(code, _code)

        # Check the data
        self.assertIsNotNone(data)
        
        # Check the data content
        self.assertEqual(data.get_stations()[0].get('code'), 'KBN')

        # Check if unsupported options are removed from the URL
        self.assertEqual(url, "http://orfeus-eu.org/odcws/rrsm/1/"
                         "shakemap?eventid=20170524_0000045")

    def test_query_event_data(self):
        # Test the query method.
        client = RRSMShakeMapWebService()
        client.set_agency("ORFEUS")
        client.set_version("1")
        client.set_end_point("shakemap")
        client.set_base_url("http://orfeus-eu.org/odcws/rrsm/")
        url = client.build_url(eventid='20170524_0000045', type='event')
        code, data = client.query(url=url)
        
        # Check if unsupported options are removed from the URL
        self.assertEqual(url, "http://orfeus-eu.org/odcws/rrsm/1/"
                         "shakemap?eventid=20170524_0000045&type=event")
        
        # Check the query against common error codes. 
        if code != 503:
            # Service is avaliable, so these error should not be returned
            # if data is not removed from the ESM server. In that case, the
            # error code will be 404.
            for _code in [400, 404, 500, 501, 502]:
                self.assertNotEqual(code, _code)

        # Check the data
        self.assertIsNotNone(data)
        
        # Check the data content. The id and coordinates are different
        # than those from EMSC, so excluded from the test. Also, there
        # is no 'catalog' key in the data.
        self.assertAlmostEqual(data.get('lat'), 41.53)
        self.assertAlmostEqual(data.get('lon'), 20.22)
        self.assertAlmostEqual(data.get('depth'), 14)
        self.assertAlmostEqual(data.get('mag'), 4.6)
        
        