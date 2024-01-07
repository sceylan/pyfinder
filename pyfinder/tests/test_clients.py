# -*- coding: utf-8 -*-
"""Unit tests for the base client class."""
import unittest
import os
import sys

module_path = os.path.abspath(__file__)
one_up = os.path.join(module_path, '..')
one_up = os.path.abspath(one_up)
sys.path.append(one_up)

from clients.baseclient import BaseWebServiceClient, \
    InvalidQueryOption, InvalidOptionValue
from clients.esm.shakemap_client import ESMShakeMapClient

class TestBaseClient(unittest.TestCase):
    """Unit tests for the base client class."""

    def test_set_get_data(self):
        # Test the set_data method.
        try:
            base_client = BaseWebServiceClient()
            base_client.set_data("test")
            self.assertEqual(base_client.data, "test")
            self.assertEqual(base_client.get_data(), "test")

        except TypeError:
            # TypeError will be raised because the class is abstract.
            # We know that, so we can pass.
            pass

    def test_add_field(self):
        # Test add_field method.
        try:
            base_client = BaseWebServiceClient()
            base_client.add_field("field1", "value1")
            self.assertEqual(base_client.get("field1"), "value1")

        except TypeError:
            # TypeError will be raised because the class is abstract.
            # We know that, so we can pass.
            pass

    
class TestESMShakeMapClient(unittest.TestCase):
    """Unit tests for the ESM Shakemap web service client."""
    def test_url_build(self):
        # Test the build_url method.
        client = ESMShakeMapClient()
        client.set_agency("ESM")
        client.set_version("1")
        client.set_end_point("shakemap")
        client.set_base_url("https://esm-db.eu/esmws")
        url = client.build_url()
        self.assertEqual(url, "https://esm-db.eu/esmws/shakemap/1/query?")


    def test_url_build_with_options(self):
        # Test the build_url method with valid, several options.
        client = ESMShakeMapClient()
        client.set_agency("ESM")
        client.set_version("1")
        client.set_end_point("shakemap")
        client.set_base_url("https://esm-db.eu/esmws")
        url = client.build_url(eventid="test_id")
        self.assertEqual(url, "https://esm-db.eu/esmws/shakemap/1/query?"
                         "eventid=test_id")

        # Test with several valid flags
        url = client.build_url(eventid="test_id", format="event_dat", catalog="ESM")
        self.assertEqual(url, "https://esm-db.eu/esmws/shakemap/1/query?"
                         "eventid=test_id&format=event_dat&catalog=ESM")


    def test_url_build_invalid_flags(self):
        # Test the build_url with invalid flags.
        client = ESMShakeMapClient()
        client.set_agency("ESM")
        client.set_version("1")
        client.set_end_point("shakemap")
        client.set_base_url("https://esm-db.eu/esmws")
        options = dict(eventid="test_id", format="event_dat", 
                       catalog="ESM", uknown_flag="not_a_valid_value")
        
        # Should throw and InvalidQueryOption exception because of the
        # "unknown flag".
        self.assertRaises(InvalidQueryOption, client.build_url, **options)
        

    def test_url_build_invalid_value(self):
        # Test the build_url with invalid flags.
        client = ESMShakeMapClient()
        client.set_agency("ESM")
        client.set_version("1")
        client.set_end_point("shakemap")
        client.set_base_url("https://esm-db.eu/esmws")
        options = dict(
            eventid="test_id", format="event_dat", catalog="Unknown")
        
        # Should throw and InvalidOptionValue exception because of the
        # catalog="Unknown" is not in the allowed values.
        self.assertRaises(InvalidOptionValue, client.build_url, **options)
    

    def test_query_options(self):
        # Test the get_supported_options method.
        client = ESMShakeMapClient()
        options = client.get_supported_options()
        self.assertEqual(options, ['eventid', 'catalog', 'format', 'flag', 'encoding'])
        

    def test_query(self):
        # Test the query method.
        client = ESMShakeMapClient()
        client.set_agency("ESM")
        client.set_version("1")
        client.set_end_point("shakemap")
        client.set_base_url("https://esm-db.eu/esmws")
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
        self.assertEqual(data.get_stations()[0].get('code'), 'KRK1')
        