# -*- coding: utf-8 -*-
import datetime
import xmltodict
from ..baseparser import BaseParser
from ..shakemap_data import ShakeMapEventData
from ..shakemap_data import ShakeMapStationAmplitudes
from ..shakemap_data import ShakeMapStationNode
from ..shakemap_data import ShakeMapComponentNode

class ESMShakeMapParser(BaseParser):
    """
    Parser class for the ESM ShakeMap web service output.
    The return from the web service is an XML file without
    and style sheet. The parser converts the XML file to
    a dictionary, and then creates a data structure.
    """
    def __init__(self):
        super().__init__()

    def _parse_amplitudes(self, data)->ShakeMapStationAmplitudes:
        """
        Parse the data returned by the ESM ShakeMap web service.
        This method converts the XML content to a dictionary only
        for format="event_dat". 
        """
        self.set_original_content(content=data)

        # Convert the XML content to a dictionary. 
        # This is easier to work with.
        xml_content = xmltodict.parse(data)

        # Initialize the main data structure for the ESM ShakeMap.
        # The top-level data structure is a dictionary with two keys:
        # - created: The creation time of the data.
        # - stations: A list of stations.
        try:
            _creation_time = datetime.datetime.fromtimestamp(
                    int(xml_content['stationlist']['@created']))
        except:
            _creation_time = datetime.datetime.now()
        
        _esm_toplevel_data = {"created": _creation_time, "stations": []}
        esm_shakemap_data = ShakeMapStationAmplitudes(_esm_toplevel_data)

        for _sta in xml_content['stationlist']['station']:
             # Station ID is constructed using network and station code 
            # to search for the station in station list
            _id = "{}.{}".format(_sta['@netid'], _sta['@code'])

            # Each station is a dictionary of attributes, and contains
            # another list for the components
            my_keys = ['name', 'code', 'netid', 'source', 'insttype', 
                       'lat', 'lon']
            keys_in_xml = ['@name', '@code', '@netid', '@source', 
                           '@insttype', '@lat', '@lon']
            station = {'id': _id, 'components': []}
            for my_key, real_key in zip(my_keys, keys_in_xml):
                try:
                    station[my_key] = _sta[real_key]
                except:
                    station[my_key] = None
            
            # Create a station-level dictionary (in reality, a wrapper 
            # around the dictionary)
            station_node = ShakeMapStationNode(data_dict=station)

            # Add the station node to the main data structure
            esm_shakemap_data.stations.append(station_node)

            # Each component is again a dictionary
            keys = ['depth', 'acc', 'vel', 'psa03', 'psa10', 'psa30']            
            if 'comp' in _sta:
                for _comp in _sta['comp']:
                    component = {'name': _comp['@name']}

                    for key in keys:
                        try:
                            component[key] = float(_comp[key]['@value'])
                            component[key + 'flag'] = int(_comp[key]['@flag'])
                        except:
                            if key == 'depth':
                                component[key] = 0.0
                            else:
                                component[key] = None

                    # Create a channel-level dictionary
                    channel_node = ShakeMapComponentNode(data_dict=component)

                    # Add the channel node to the station node
                    station_node.components.append(channel_node)

        # Pass the main data structure back to the caller
        return esm_shakemap_data
    
    def parse(self, data)->ShakeMapStationAmplitudes:
        """
        Calls the internal parsing method for format="event_dat" option
        if the data is successfully validated. 
        """
        if data and self.validate(data):
            return self._parse_amplitudes(data)
        else:
            raise ValueError("Invalid data. The content is not " +
                             "a valid ESM Shakemap XML file.")        

    def validate(self, data):
        """Check the content of the data."""
        return True
    
    def parse_earthquake(self, data)->ShakeMapEventData:
        """ 
        Parse the data returned by the ESM ShakeMap web service 
        when format='event'. Called by the parse_response() method
        of the ESM ShakeMap client.
        """
        if data and self.validate(data):
            # Store the original content
            self.set_original_content(content=data)

            # Convert the XML content to a dictionary.
            xml_content = xmltodict.parse(data)

            eq = xml_content['earthquake']

            # The keys in the dictionary 
            keys = ['id', 'catalog', 'lat', 'lon', 'depth', 'mag', 'year', 
                    'month', 'day', 'hour', 'minute', 'second', 'timezone', 
                    'time', 'locstring', 'netid', 'network', 'created']
            event_data = {}

            for key in keys:
                if '@' + key in eq:
                    if key in ['lat', 'lon', 'depth', 'mag', 'second']:
                        event_data[key] = float(eq['@' + key])
                    elif key in ['year', 'month', 'day', 'hour', 'minute']:
                        event_data[key] = int(eq['@' + key])
                    else:
                        event_data[key] = eq['@' + key]
                else:
                    event_data[key] = None

            # Create a ShakeMapEventData object            
            esm_shakemap_data = ShakeMapEventData(event_data)

            return esm_shakemap_data
