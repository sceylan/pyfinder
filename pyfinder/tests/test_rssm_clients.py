# -*- coding: utf-8 -*-
"""Unit tests for the base client class."""
import unittest
import os
import sys

module_path = os.path.abspath(__file__)
one_up = os.path.join(module_path, '..')
one_up = os.path.abspath(one_up)
sys.path.append(one_up)

from clients.rrsm.shakemap_client import RRSMShakeMapClient
from clients.baseclient import InvalidQueryOption

class TestRRSMShakeMapClient(unittest.TestCase):
    """Unit tests for the RRSM Shakemap web service client."""
    def test_url_build(self):
        # Test the build_url method.
        client = RRSMShakeMapClient()
        client.set_version("1")
        client.set_end_point("shakemap")
        client.set_base_url("http://orfeus-eu.org/odcws/rrsm/")
        url = client.build_url()
        self.assertEqual(url, "http://orfeus-eu.org/odcws/rrsm/1/shakemap?")

    def test_query_options(self):
        # Test the get_supported_options method.
        client = RRSMShakeMapClient()
        options = client.get_supported_options()
        self.assertEqual(options, ['eventid'])

    def test_url_build_with_valid_options(self):
        # Test the build_url method with valid, several options.
        client = RRSMShakeMapClient()
        client.set_version("1")
        client.set_end_point("shakemap")
        client.set_base_url("http://orfeus-eu.org/odcws/rrsm/")
        url = client.build_url(eventid="test_id")
        self.assertEqual(
            url, "http://orfeus-eu.org/odcws/rrsm/1/shakemap?eventid=test_id")


    def test_query_format_eventdat(self):
        # Test the query method.
        client = RRSMShakeMapClient()
        client.set_agency("ORFEUS")
        client.set_version("1")
        client.set_end_point("shakemap")
        client.set_base_url("http://orfeus-eu.org/odcws/rrsm/")
        url = client.build_url(eventid='20170524_0000045', catalog='EMSC', format='event_dat')
        code, data = client.query(url=url)

        # Check against common error codes. 
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
        
