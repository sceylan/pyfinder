# -*- coding: utf-8 -*-
"""Unit tests for the base client class."""
import unittest
from clients.services import InvalidOptionValue
from clients.services import ESMShakeMapWebService

class TestESMShakeMapWebService(unittest.TestCase):
    """Unit tests for the ESM Shakemap web service client."""
    def test_url_build(self):
        # Test the build_url method.
        client = ESMShakeMapWebService()
        client.set_agency("ESM")
        client.set_version("1")
        client.set_end_point("shakemap")
        client.set_base_url("https://esm-db.eu/esmws")
        url = client.build_url()
        self.assertEqual(url, "https://esm-db.eu/esmws/shakemap/1/query?")


    def test_url_build_with_valid_options(self):
        # Test the build_url method with valid, several options.
        client = ESMShakeMapWebService()
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


    def test_url_build_invalid_options(self):
        # Test the build_url with invalid flags.
        client = ESMShakeMapWebService()
        client.set_agency("ESM")
        client.set_version("1")
        client.set_end_point("shakemap")
        client.set_base_url("https://esm-db.eu/esmws")
        options = dict(eventid="test_id", format="event_dat", 
                       catalog="ESM", uknown_flag="not_a_valid_value")
        
        # build_url does an internal clean-up for invalid options.
        # So, the uknown_flag should be removed from the url. An 
        # InvalidQueryOption exception will be raised if something 
        # goes wrong with the clean-up at the end.
        url = client.build_url(**options)
       
    def test_url_build_invalid_value(self):
        # Test the build_url with invalid flags.
        client = ESMShakeMapWebService()
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
        client = ESMShakeMapWebService()
        options = client.get_supported_options()
        self.assertEqual(options, ['eventid', 'catalog', 'format', 'flag', 'encoding'])
        

    def test_query_format_eventdat(self):
        # Test the query method.
        client = ESMShakeMapWebService()
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
        
      
    def test_query_format_event(self):
        # Test the query method.
        client = ESMShakeMapWebService()
        client.set_agency("ESM")
        client.set_version("1")
        client.set_end_point("shakemap")
        client.set_base_url("https://esm-db.eu/esmws")
        url = client.build_url(eventid='20170524_0000045', catalog='EMSC', format='event')
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
        self.assertEqual(data.get('id'), '20170524_0000045')
        self.assertAlmostEqual(data.get('catalog'), 'EMSC')
        self.assertAlmostEqual(data.get('lat'), 41.422832)
        self.assertAlmostEqual(data.get('lon'), 20.155666)
        self.assertAlmostEqual(data.get('depth'), 9.28)
        self.assertAlmostEqual(data.get('mag'), 4.5)
