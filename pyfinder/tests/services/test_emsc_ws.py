# -*- coding: utf-8 -*-
"""Unit tests for the base client class."""
import unittest
from clients.services import EMSCFeltReportWebService

class TestEMSCFeltReportWebService(unittest.TestCase):
    """Unit tests for the RRSM Shakemap web service client."""
    def test_supported_options(self):
        # Test the get_supported_options method.
        client = EMSCFeltReportWebService()
        options = client.get_supported_options()
        self.assertEqual(options, ['unids', 'includeTestimonies'])

    def test_url_build(self):
        # Test the build_url method.
        client = EMSCFeltReportWebService()
        client.set_version("1.1")
        client.set_end_point("api")
        client.set_base_url("https://www.seismicportal.eu/testimonies-ws")
        url = client.build_url()
        self.assertEqual(url, "https://www.seismicportal.eu/testimonies-ws/api/search?")

    def test_rename_option(self):
        # Test the build_url method.
        client = EMSCFeltReportWebService()
        client.set_version("1.1")
        client.set_end_point("api")
        client.set_base_url("https://www.seismicportal.eu/testimonies-ws")
        url = client.build_url(includetestimonies="true")
        self.assertEqual(url, "https://www.seismicportal.eu/testimonies-ws/api/"
            "search?includeTestimonies=true")
