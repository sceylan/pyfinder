# -*- coding: utf-8 -*-
import unittest
import os
import sys
import zipfile
module_path = os.path.dirname(os.path.abspath(__file__))
one_up = os.path.join(module_path, '..')
sys.path.append(one_up)
from clients.services.emsc.feltreport_parser import EMSCFeltReportParser


class TestEMSCShakeMapParser(unittest.TestCase):
    """ Test the parser for ESM ShakeMap web service. """
    def test_EMSC_parse_testimonies(self):
        # Test if the downlinked zip file is handled properly.
        zip_path = os.path.join(
            module_path, 'testdata', 'mt-export-single.zip')
        
        with zipfile.ZipFile(zip_path) as zip:
            parser = EMSCFeltReportParser()
            parsed_data = parser.parse_testimonies(zip)

            # data should not be None or empty. The test file
            # contains testomines for a single earthquake.
            self.assertIsNotNone(parsed_data)
            self.assertIsNotNone(parsed_data.get_data())
            self.assertNotEqual(len(parsed_data.get_data()), 0)

    def test_EMSC_intensities_integrity(self):
        # Test if the intensities correctly parsed. 
        zip_path = os.path.join(
            module_path, 'testdata', 'mt-export-single.zip')
        
        with zipfile.ZipFile(zip_path) as zip:
            parser = EMSCFeltReportParser()
            parsed_data = parser.parse_testimonies(zip)

            # Check the event id
            for key, _ in parsed_data.get_data().items():
                self.assertEqual(
                    parsed_data.get_data()[key]['unid'], '20201230_0000049')

            # Check the intensities: make sure we have four columns
            unid = parsed_data.get_data()[key]['unid']
            self.assertEqual(len(parsed_data.get_data()[unid]['intensities'][0]), 4)

            # Check field names for intensities
            intensity = parsed_data.get_data()[unid]['intensities'][0]
            self.assertEqual(intensity.keys(), {'lon', 'lat', 'raw', 'corrected'})

            # Check the first intensity
            # lon:14.4824, lat: 46.0752, raw: 1, corrected: 1
            self.assertAlmostEqual(intensity['lon'], 14.4824)
            self.assertAlmostEqual(intensity['lat'], 46.0752)
            self.assertAlmostEqual(intensity['raw'], 1)
            self.assertAlmostEqual(intensity['corrected'], 1)
    