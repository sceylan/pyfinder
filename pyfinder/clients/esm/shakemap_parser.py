# -*- coding: utf-8 -*-
import datetime
import xmltodict
from ..baseparser import BaseParser
from ..shakemap_data import ShakeMapData
from ..shakemap_data import ShakeMapDataStationNode
from ..shakemap_data import ShakeMapDataComponentNode

class ESMShakeMapParser(BaseParser):
    """
    Parser class for the ESM ShakeMap web service output.
    The return from the web service is an XML file without
    and style sheet. The parser converts the XML file to
    a dictionary, and then creates a data structure.
    """
    def __init__(self):
        super().__init__()

    def _parse_amplitudes(self, data):
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
        esm_shakemap_data = ShakeMapData(_esm_toplevel_data)

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
            station_node = ShakeMapDataStationNode(data_dict=station)

            # Add the station node to the main data structure
            esm_shakemap_data.stations.append(station_node)

            # Each component is again a dictionary
            if 'comp' in _sta:
                for _comp in _sta['comp']:
                    component = {'name': _comp['@name']}
                    # Depth if available or None
                    try:
                        component['depth'] = float(_comp['@depth'])
                    except:
                        component['depth'] = None

                    # Acceleration, velocity, and PSA values with their
                    # quality flags. If any of the the values is not available
                    # or something is not correct with type casting, set it to None
                    try:
                        component['acc'] = float(_comp['acc']['@value'])
                        component['accflag'] = int(_comp['acc']['@flag'])
                    except:
                        component['acc'] = None
                        component['accflag'] = None
     
                    try:
                        component['vel'] = float(_comp['vel']['@value'])
                        component['velflag'] = int(_comp['vel']['@flag'])
                    except:
                        component['vel'] = None
                        component['velflag'] = None

                    try:
                        component['psa03'] = float(_comp['psa03']['@value'])
                        component['psa03flag'] = int(_comp['psa03']['@flag'])
                    except:
                        component['psa03'] = None
                        component['psa03flag'] = None

                    try:
                        component['psa10'] = float(_comp['psa10']['@value'])
                        component['psa10flag'] = int(_comp['psa10']['@flag'])
                    except:
                        component['psa10'] = None
                        component['psa10flag'] = None

                    try:
                        component['psa30'] = float(_comp['psa30']['@value'])
                        component['psa30flag'] = int(_comp['psa30']['@flag'])
                    except:
                        component['psa30'] = None
                        component['psa30flag'] = None
                        
                    # Create a channel-level dictionary
                    channel_node = ShakeMapDataComponentNode(data_dict=component)

                    # Add the channel node to the station node
                    station_node.components.append(channel_node)

        # Pass the main data structure back to the caller
        return esm_shakemap_data
    
    def parse(self, data):
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
    
    def parse_earthquake(self, data):
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
            event_data = {'id': eq['@id'], 'catalog': eq['@catalog'], 
                          'lat': float(eq['@lat']), 'lon': float(eq['@lon']), 
                          'depth': float(eq['@depth']), 'mag': float(eq['@mag']), 
                          'year': eq['@year'], 'month': eq['@month'],
                          'day': eq['@day'], 'hour': eq['@hour'], 
                          'minute': eq['@minute'], 'second': eq['@second'], 
                          'timezone': eq['@timezone'], 'time': eq['@time'], 
                          'locstring': eq['@locstring'], 'netid': eq['@netid'], 
                          'network': eq['@network'], 'created': eq['@created']}
            
            esm_shakemap_data = ShakeMapData(event_data)

            return esm_shakemap_data
        