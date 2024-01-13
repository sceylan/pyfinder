# -*- coding: utf-8 -*-
import unittest
import os
import sys
module_path = os.path.dirname(os.path.abspath(__file__))
one_up = os.path.join(module_path, '..')
sys.path.append(one_up)
from clients.services.esm.shakemap_parser import ESMShakeMapParser

# Some real data from the ESM ShakeMap web service for testing.
station_list = {
    "HL.KASA": {},
    "HL.JAN": {},
    "HI.LMS2": {},
    "HI.KRK1": {
        "code": "KRK1",
        "name": "KRK1",
        "netid": "HI",
        "source": "ITSAK Strong Motion Network",
        "insttype": "",
        "lat": "39.618861",
        "lon": "19.9202",
        "comp": [
            {"name": ".HNE", "depth": "0.0",
             "acc": {"value": "0.016794504", "flag": "0"},
             "vel": {"value": "0.008192","flag": "0"},
             "psa03": {"value": "0.0394178840307","flag": "0"},
             "psa10": {"value": "0.00614489465695","flag": "0"},
             "psa30": {"value": "0.00123846427919","flag": "0"}},
            
            {"name": ".HNN", "depth": "0.0",
             "acc": {"value": "0.016320204", "flag": "0"},
             "vel": {"value": "0.008136","flag": "0"},
             "psa03": {"value": "0.0418339631881", "flag": "0"},
             "psa10": {"value": "0.007030790348", "flag": "0"},
             "psa30": {"value": "0.000478741610816", "flag": "0"}},
            
            {"name": ".HNZ", "depth": "0.0",
             "acc": {"value": "0.018035436", "flag": "0"},
             "vel": {"value": "0.002963", "flag": "0"},
             "psa03": {"value": "0.0272927460371", "flag": "0"},
             "psa10": {"value": "0.00361203834029", "flag": "0"},
             "psa30": {"value": "0.000409391190557", "flag": "0"}}]}
}

class TestESMShakeMapParser(unittest.TestCase):
    """ Test the parser for ESM ShakeMap web service. """
    def test_ESMShakeMap_parser_format_event(self):
        # Test the parser for the ESM ShakeMap web service when format="event".
        xml_path = os.path.join(module_path, 'testdata', 'esmws-event.xml')
        with open(xml_path, 'r') as xmlfile:
            data = xmlfile.read()
            parser = ESMShakeMapParser()
            eq_data = parser.parse_earthquake(data)

            # Check the earthquake data against some of the attributes.
            self.assertEqual(eq_data['id'], '20170524_0000045')
            self.assertAlmostEqual(eq_data['lat'], 41.422832)
            self.assertAlmostEqual(eq_data['lon'], 20.155666)
            self.assertAlmostEqual(eq_data['depth'], 9.28)
            self.assertAlmostEqual(eq_data['mag'], 4.5)
            self.assertEqual(eq_data['time'], '2017-05-24T10:30:59Z')            

    def test_ESMShakeMap_parser_format_eventdat(self):
        # Test the parser for the ESM ShakeMap web service when format="event_dat".
        xml_path = os.path.join(module_path, 'testdata', 'esmws-eventdata.xml')
        with open(xml_path, 'r') as xmlfile:
            data = xmlfile.read()
            parser = ESMShakeMapParser()
            shakemap_data = parser.parse(data)

            for station in shakemap_data.get_stations():
                # Check if the station ID is in the test data. The id is made
                # up of network and station code by the parser. I manually
                # add this field as the key to the test dictionary.
                # This test includes testing the subscripting method of the
                # data structure.
                if station['id'] not in station_list:
                    self.fail("Station {} not found in the test data.".format(
                        station['id']))
                    
                # Check with a single station in detail. In this test case,
                # we also testing the get() method of the data structure.
                # We also keep track of which components have been visited.
                # This is to make sure that all components are tested.
                _visited = {'.HNZ': False, '.HNN': False, '.HNE': False}

                if station.get('id') == 'HI.KRK1':
                    for component in station.get('components'):
                        if component.get('name') == '.HNE':
                            # Test with the get() method of the data structure.
                            self.assertAlmostEqual(component.get('acc'), 0.016794504)
                            self.assertEqual(component.get('accflag'), 0)
                            self.assertEqual(component.get('depth'), 0.0)
                            self.assertEqual(component.get('name'), '.HNE')
                            self.assertAlmostEqual(component.get('psa03'), 0.0394178840307)
                            self.assertEqual(component.get('psa03flag'), 0)
                            self.assertAlmostEqual(component.get('psa10'), 0.00614489465695)
                            self.assertEqual(component.get('psa10flag'), 0)
                            self.assertAlmostEqual(component.get('psa30'), 0.00123846427919)
                            self.assertEqual(component.get('psa30flag'), 0)
                            self.assertAlmostEqual(component.get('vel'), 0.008192)
                            self.assertEqual(component.get('velflag'), 0)
                            _visited['.HNE'] = True

                        elif component.name == '.HNN':
                            # With this component, test the dot notation for 
                            # getting the values assigned to a dict key.
                            self.assertAlmostEqual(component.acc, 0.016320204)
                            self.assertEqual(component.accflag, 0)
                            self.assertEqual(component.depth, 0.0)
                            self.assertEqual(component.name, '.HNN')
                            self.assertAlmostEqual(component.psa03, 0.0418339631881)
                            self.assertEqual(component.psa03flag, 0)
                            self.assertAlmostEqual(component.psa10, 0.007030790348)
                            self.assertEqual(component.psa10flag, 0)
                            self.assertAlmostEqual(component.psa30, 0.000478741610816)
                            self.assertEqual(component.psa30flag, 0)
                            self.assertAlmostEqual(component.vel, 0.008136)
                            self.assertEqual(component.velflag, 0)
                            _visited['.HNN'] = True

                        elif component['name'] == '.HNZ':
                            # Test with the subscripting method of the data
                            self.assertAlmostEqual(component['acc'], 0.018035436)
                            self.assertEqual(component['accflag'], 0)
                            self.assertEqual(component['depth'], 0.0)
                            self.assertEqual(component['name'], '.HNZ')
                            self.assertAlmostEqual(component['psa03'], 0.0272927460371)
                            self.assertEqual(component['psa03flag'], 0)
                            self.assertAlmostEqual(component['psa10'], 0.003612038340)
                            self.assertEqual(component['psa10flag'], 0)
                            self.assertAlmostEqual(component['psa30'], 0.000409391190557)
                            self.assertEqual(component['psa30flag'], 0)
                            self.assertAlmostEqual(component['vel'], 0.002963)
                            self.assertEqual(component['velflag'], 0)
                            _visited['.HNZ'] = True

                        else:
                            self.fail("Unknown component name: {}".format(
                                component.get('name')))

                    # Check if all components have been visited.
                    for key in _visited.keys():
                        if not _visited[key]:
                            self.fail("Component {} not visited.".format(key))
