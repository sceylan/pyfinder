# -*- coding: utf-8 -*-
import datetime
import xmltodict

import sys
sys.path.append("..")
from baseparser import BaseParser
from clients.esm.shakemap_data import ESMEventWSData
from clients.esm.shakemap_data import ESMEventWSOriginNode
from clients.esm.shakemap_data import ESMEventWSMagnitudeNode
from clients.esm.shakemap_data import ESMEventWSFocalMechanismNode
from clients.esm.shakemap_data import ESMEventWSMomentTensorNode

class ESMEventWSParser(BaseParser):
    """
    Parser class for the ESM Event web service output.
    The return from the web service is a QuakeML XML. 
    This parser converts the XML file to a dictionary, 
    then creates a data structure.
    """
    def __init__(self):
        super().__init__()

    def _parse(self, data):
        """Parse the data returned by the ESM Event web service."""
        self.set_original_content(content=data)

        # Convert the XML content to a dictionary. This is easier
        # to work with.
        quakeml_dict = xmltodict.parse(data)

        # Initialize the main data structure for the ESM Event end point.
        _esm_toplevel_data = {
            "created": datetime.datetime.fromtimestamp(
                int(quakeml_dict['stationlist']['@created'])),
            "stations": []}
        esm_shakemap_data = ESMEventWSData(_esm_toplevel_data)

        # Extract and print information for all events
        event_parameters = quakeml_dict['q:quakeml']['eventParameters']
        events = event_parameters.get('event', [])

        for event in events:
            event_id = event['@publicID']
            
            # Extract details for the event
            origin = event.get('origin', {})
            magnitude = event.get('magnitude', {}).get('mag', None)
            focal_mechanism = event.get('focalMechanism', {})
            moment_tensor = focal_mechanism.get('momentTensor', {})
            nodal_planes = focal_mechanism.get('nodalPlanes', {}).get('nodalPlane', [])

            # This is an example
            for i, nodal_plane in enumerate(nodal_planes):
                print(f"  Nodal Plane {i + 1}:")
                print("    Strike:", nodal_plane.get('strike', {}).get('value', 'N/A'))
                print("    Dip:", nodal_plane.get('dip', {}).get('value', 'N/A'))
                print("    Rake:", nodal_plane.get('rake', {}).get('value', 'N/A'))


        # Pass the main data structure back to the caller
        return esm_shakemap_data
    
    def parse(self, data):
        """
        Calls the internal parse method if the data 
        is successfully validated.
        """
        if self.validate(data):
            return self._parse(data)
        else:
            raise ValueError("Invalid data. The content is not " +
                             "a valid QuakeML file from ESM.")        

    def validate(self, data):
        """Check the content of the data."""
        return True